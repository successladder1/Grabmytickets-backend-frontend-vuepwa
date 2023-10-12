from operator import and_, or_
from application.jobs.workers import celery
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import datetime
from flask import Flask, abort, jsonify, make_response, render_template, request, session, redirect, flash, url_for, send_file
from flask_restful import Api, Resource
import os
from application.jobs import tasks
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from flask_security import login_required, roles_accepted, roles_required, login_user, logout_user
from application.data.models import *
from sqlalchemy.orm import aliased
with open('config.json', 'r') as c:
    params = json.load(c)['params']
from flask_sse import sse
from celery.result import AsyncResult

@app.route("/")
def hello():
    return render_template("index.html")

# A search function that allows the user to search for movies and venues but only after logging in.
@app.route('/search/<user_id>', methods=["GET", "POST"])
def search_results(user_id):
    query = request.form.get('query')
    category = request.form.get('category')
    user=User.query.filter_by(user_id=user_id).first()
    print(f"query: {query}, category: {category}")
    current_time = datetime.datetime.now()
    if category == 'venue':
        venues = Venue.query.filter(Venue.city.ilike(f'%{query}%')).all()
        movies_by_venue = {}
        current_time = datetime.datetime.now()
        for venue in venues:
            movies = Movie.query.join(movie_venue).filter_by(
                venue_id=venue.venue_id).order_by(movie_venue.time.asc()).all()
            current_movies = []
            for movie in movies:
                mv_object= movie_venue.query.filter_by(movie_id=movie.movie_id, venue_id=venue.venue_id).first()
                mvtime=datetime.datetime.strptime(mv_object.time, '%d:%m:%Y %H:%M:%S')

                if mvtime > current_time:
                    current_movies.append((movie, mv_object))
            if current_movies:
                movies_by_venue[venue.venue_id] = current_movies
        return render_template('search_results.html', user=user, venues=venues, movies_by_venue=movies_by_venue, category='venue', query=query)

    elif category == 'movie':
        current_time = datetime.datetime.now()
        movies = Movie.query.filter(Movie.title.ilike(f'%{query}%')).all()
        print(f"results: {movies}")
        movie_venues = movie_venue.query.join(Movie).join(Venue).\
            filter(Movie.title.ilike(f'%{query}%')).all()

        # Group the movie-venue pairs by movie
        movies = {}
        for mv in movie_venues:
            mvtime=datetime.datetime.strptime(mv.time, '%d:%m:%Y %H:%M:%S')
            if mvtime > current_time:
                movie_id = mv.movie_id
                if movie_id not in movies:
                    movies[movie_id] = {
                        'movie': mv.movie,
                        'venues': []
                    }
            movies[movie_id]['venues'].append(mv.venue)
        movies = list(movies.values())

        print(f"results: {movies}")
        return render_template('search_results.html', movies=movies, query=query, user=user,category='movie')

    else:
        flash('Invalid search category')
        return redirect(url_for('hello'))

#The admin login page that gets both GET and POST requests
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if "admin" in session and session["admin"] == params["admin_username"]:
        venues = Venue.query.all()
        return render_template("admin_dashboard.html", params=params, venues=venues)
    if request.method == "POST":
        username = request.form.get("admin_username")
        password = request.form.get("admin_password")
        if (username == params['admin_username'] and password == params['admin_password']):
            flash(' Admin Loggedin successfully')
            session['admin'] = username
            venues = Venue.query.all()
            return redirect("/admin_dashboard")
        elif (username == params['admin_username'] and password != params['admin_password']):
            flash('Password mismatch. Please enter the correct password!')
            return redirect('/admin_login')
        elif (username != params['admin_username']):
            flash('Incorrect admin username')
            return redirect('/admin_login')
    return render_template("admin_login.html", params=params)


# Shows admin dashboard where all the existing venues and their attributes are listed and contains buttons for implementing crud on venues.
#The admin dashboard also has a search bar that allows the admin to search for venues.
@app.route("/admin_dashboard")
def admin_dashboard():
    # Fetch data from the database
    search_query = request.args.get('search', default='', type=str)
    if search_query:
        venues = Venue.query.filter(or_(Venue.name.ilike(f"%{search_query}%"), Venue.city.ilike(f"%{search_query}%"))).all()
    else:
        venues = Venue.query.all()
    # Render the admin dashboard template with the fetched data
    return render_template("admin_dashboard.html", params=params, venues=venues)

# THE GET, PUT AND POST OPERATIONS ON VENUE (CRU)
@app.route("/edit/<venue_id>", methods=["GET", "POST"])
def edit_venue(venue_id):
    if "admin" in session and session["admin"] == params["admin_username"]:
        if request.method == "POST":
            name = request.form.get("name")
            address = request.form.get("address")
            city = request.form.get("city")
            state = request.form.get("state")
            country = request.form.get("country")
            # date=datetime.now()
            capacity = request.form.get("capacity")
            phone = request.form.get("phone")
            email = request.form.get("email")
            if venue_id == '0':
                venue = Venue(name=name, address=address, city=city, state=state,
                              country=country, capacity=capacity, phone=phone, email=email)
                db.session.add(venue)
                db.session.commit()
                return redirect('/admin_dashboard')
            else:
                venue = Venue.query.filter_by(venue_id=venue_id).first()
                venue.name = name
                venue.address = address
                venue.city = city
                venue.state = state
                venue.country = country
                # venue.date=date
                venue.capacity = capacity
                venue.phone = phone
                venue.email = email
                db.session.commit()
                return redirect('/admin_dashboard')
        venue = Venue.query.filter_by(venue_id=venue_id).first()
        return render_template("edit_venue.html", params=params, venue_id=venue_id, venue=venue)
    return redirect('/admin_login')

# Gets a grid consisting of all the movies present inside a particular venue
@app.route("/venue_movie_dashboard/<venue_id>")
def venue_movie_dashboard(venue_id):
    if "admin" in session and session["admin"] == params["admin_username"]:
        search_query = request.args.get('search', default='', type=str)
        if search_query:
            venue = Venue.query.filter_by(venue_id=venue_id).first()
            movie_venue_objs = movie_venue.query \
                .join(Movie) \
                .filter(movie_venue.venue_id == venue_id, Movie.title.ilike(f'%{search_query}%')) \
                .all()
        else:
            venue = Venue.query.filter_by(venue_id=venue_id).first()
            if not venue:
                return redirect('/admin_dashboard')
            movie_venue_objs = movie_venue.query.filter_by(venue_id=venue_id).all()
        return render_template('venue_movie_dashboard.html', venue=venue, movie_venue_objs=movie_venue_objs, venue_id=venue_id)
    return redirect('/admin_login')

# The GET, PUT AND POST operations on a movie inside a venue. (CRU)
@app.route("/edit_movie/<venue_id>/<movie_id>", methods=["GET", "POST"])

def edit_movie(venue_id, movie_id):
    if "admin" in session and session["admin"] == params["admin_username"]:
        if request.method == "POST":
            title = request.form.get("title")
            genre = request.form.get("genre")
            language = request.form.get("language")
            runtime = request.form.get("runtime")
            rating = request.form.get("rating")
            create_date = datetime.datetime.now()
            director = request.form.get("director")
            synopsis = request.form.get("synopsis")
            release_date = request.form.get("release_date")
            trailer_url = request.form.get("trailer_url")
            price = request.form.get("price")
            date = request.form.get("date")
            time = request.form.get("time")
            seats_available=request.form.get("seats_available")
            if movie_id == '0':
                movie = Movie(title=title, genre=genre, language=language, runtime=runtime, rating=rating,
                              director=director, synopsis=synopsis, release_date=release_date, trailer_url=trailer_url)
                db.session.add(movie)
                db.session.commit()
                if venue_id != "0":
                    venue = Venue.query.filter_by(venue_id=venue_id).first()
                    mv = movie_venue(movie_id=movie.movie_id, venue_id=venue_id, price=price,
                                     date=date, time=time, create_date=create_date, seats_available=seats_available)
                    db.session.add(mv)
                    db.session.commit()
                flash('Movie added successfully')
                return redirect(url_for('venue_movie_dashboard', venue_id=venue_id))

            else:
                movie_venue_obj = movie_venue.query.filter_by(
                    venue_id=venue_id, movie_id=movie_id).first()
                movie = Movie.query.filter_by(
                    movie_id=movie_venue_obj.movie_id).first()
                movie_venue_obj.price = price
                movie_venue_obj.date = date
                movie_venue_obj.time = time
                movie_venue_obj.seats_available = seats_available
                movie_venue_obj.create_date = create_date
                movie.title = title
                movie.genre = genre
                movie.language = language
                movie.runtime = runtime
                movie.rating = rating
                # venue.date=date
                movie.director = director
                movie.synopsis = synopsis
                movie.release_date = release_date
                movie.trailer_url = trailer_url
                db.session.commit()
                flash('Movie updated successfully')
                return redirect(url_for('venue_movie_dashboard', venue_id=venue_id))
        movie = Movie.query.filter_by(movie_id=movie_id).first()
        movie_venue_obj = movie_venue.query.filter_by(
            venue_id=venue_id, movie_id=movie_id).first()
        return render_template("edit_movie.html", params=params, venue_id=venue_id, movie=movie, movie_id=movie_id, mv=movie_venue_obj)
    return redirect('/admin_login')

#The confirmation page of delete operation on a movie inside a venue. Deleting it will also delete all the bookings associated with it.
@app.route('/confirm_delete_movie/<venue_id>/<movie_id>', methods=['GET', 'POST'])

def confirm_delete_movie(venue_id, movie_id):
    if "admin" in session and session["admin"] == params["admin_username"]:
        movie_venue_obj = movie_venue.query.filter_by(
            venue_id=venue_id, movie_id=movie_id).first()
        if not movie_venue_obj:
            flash("Movie not found.")
            return redirect('/venue_movie_dashboard/<venue_id>')
        movie = Movie.query.filter_by(
            movie_id=movie_venue_obj.movie_id).first()
        venue = Venue.query.filter_by(
            venue_id=movie_venue_obj.venue_id).first()
        bookings = Booking.query.filter_by(
            venue_id=venue_id, movie_id=movie_id).all()
        flag=0
        if bookings:
            flag=1
        return render_template('confirm_delete_movie.html',flag=flag, venue=venue, movie=movie, movie_venue_obj=movie_venue_obj, venue_id=venue_id)
    return redirect(url_for('admin_login'))

#The delete operation on a movie inside a venue. Deleting it will also delete all the bookings associated with it.
@app.route('/delete_movie/<venue_id>/<movie_id>', methods=['GET', 'POST'])
def delete_movie(venue_id, movie_id):
    if "admin" in session and session["admin"] == params["admin_username"]:
        var=venue_id
        movie_venue_obj = movie_venue.query.filter_by(
            venue_id=venue_id, movie_id=movie_id).first()
        bookings = Booking.query.filter_by(
            venue_id=venue_id, movie_id=movie_id).all()
        if bookings:
            for booking in bookings:
                db.session.delete(booking)
                db.session.commit()
        if movie_venue_obj:
            movie_obj = Movie.query.filter_by(movie_id=movie_venue_obj.movie_id).first()
            db.session.delete(movie_venue_obj)
            db.session.delete(movie_obj)
            db.session.commit()
            flash("Movie deleted successfully!")
        else:
            flash("Movie not found in this venue.")
    else:
        flash("You are not authorized to perform this action.")
    return redirect(url_for('venue_movie_dashboard', venue_id=var))

#The confirmation of delete operation on a venue. Deleting it will also delete all the bookings and movies associated with it.
@app.route('/confirm_delete_venue/<venue_id>', methods=['GET', 'POST'])
def confirm_delete_venue(venue_id):
    if "admin" in session and session["admin"] == params["admin_username"]:
        venue = Venue.query.filter_by(venue_id=venue_id).first()
        if not venue:
            flash("Venue not found.")
            return redirect('/admin_dashboard')
        movies = [movie_venue.movie for movie_venue in venue.venue_movies] if venue else []
        bookings = Booking.query.filter_by(
            venue_id=venue_id).all()
        flag=0
        if bookings:
            flag=1
        return render_template('confirm_delete_venue.html', venue=venue, movies=movies, flag=flag)
    return redirect(url_for('admin_login'))

#The delete operation on a venue. Deleting it will also delete all the bookings and movies associated with it.
@app.route('/delete_venue/<venue_id>', methods=['GET', 'POST'])
def delete_venue(venue_id):
    if "admin" in session and session["admin"] == params["admin_username"]:
        venue = Venue.query.filter_by(venue_id=venue_id).first()
        if venue:
            bookings = Booking.query.filter_by(
            venue_id=venue_id).all()
            if bookings:
                for booking in bookings:
                    db.session.delete(booking)
                    db.session.commit()
            for movie_venue_obj in venue.venue_movies:
                db.session.delete(movie_venue_obj)
                db.session.commit()
                movie_obj=Movie.query.filter_by(movie_id=movie_venue_obj.movie_id).first()
                # db.session.delete(movie.movie)/
                db.session.delete(movie_obj)
                db.session.commit()
            db.session.delete(venue)
            db.session.commit()
            flash("Venue deleted successfully!")
            return redirect('/admin_dashboard')
        else:
            flash("Venue not found.")
    else:
        flash("You are not authorized to perform this action.")
    return redirect(url_for('admin_login'))


# Admin log out and the response headers of no-cache no-store must-revalidate in order to not keep the admin signed it after logging out when he presses the back button.
# @app.route("/admin_logout")
# def admin_logout():
#     flash('Admin logged out successfully')
#     session.pop('admin')
#     response = make_response(redirect('/'))
#     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     return response

@app.route("/admin_logout")
@login_required
@roles_required('admin')
def admin_logout():
    logout_user()
    flash("Admin logged out successfully")
    return redirect("/admin_login")
# User login and and register page.
@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        # LOGIN IF ALREADY EXISTS
        if 'login' in request.form:
            username = request.form.get("user_username")
            password = request.form.get("user_password")
            user = User.query.filter_by(username=username).first()
            if user:
                if user.password == password:
                    session['user'] = username
                    print(user.user_id)
                    return redirect(url_for('user_dashboardd', user_id=user.user_id)) #params=params, username=username, venues=venues, movies_by_venue=movies_by_venue, user=user)
                else:
                    flash('Password mismatch')
                    return redirect('/user_login')
            else:
                flash('Username is not registered. Please register')
                return redirect('/user_login')
        #REGISTER FOR NEW USER
        if 'register' in request.form:
            username = request.form.get("user_username")
            password = request.form.get("user_password")
            user = User.query.filter_by(username=username).first()
            if user:
                flash('User already registered. Please signin')
                return redirect('/user_login')
            else:
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                flash('Successfully registered. Please signin')
    return render_template('user_login.html')

# User dashboard having cards of venues consisting of shows with a book button. 
@app.route('/user_dashboard/<user_id>')

def user_dashboardd(user_id):
    print("user_id:", user_id)
    if "user" in session:
        user = User.query.filter_by(user_id=user_id).first()
        venues = Venue.query.all()
        movies_by_venue = {}
        current_time = datetime.datetime.now()
        for venue in venues:
            movies = Movie.query.join(movie_venue).filter_by(
                venue_id=venue.venue_id).order_by(movie_venue.time.asc()).all()
            current_movies = []
            for movie in movies:
                mv_object= movie_venue.query.filter_by(movie_id=movie.movie_id, venue_id=venue.venue_id).first()
                mvtime=datetime.datetime.strptime(mv_object.time, '%d:%m:%Y %H:%M:%S')

                if mvtime > current_time:
                    current_movies.append((movie, mv_object))
            if current_movies:
                movies_by_venue[venue.venue_id] = current_movies
        return render_template('search_results.html', user=user, venues=venues, movies_by_venue=movies_by_venue, category='venue')
    return redirect('/user_login') 

# Clicking on a particular venue on search_results.html will bring a basic home view of venue where the venue details along with movies with their details are present.
@app.route('/venue_details/<user_id>/<venue_id>')
def venue_details(user_id,venue_id):
    if "user" in session:
        current_time = datetime.datetime.now()
        user = User.query.filter_by(user_id=user_id).first()
        venue=Venue.query.filter_by(venue_id=venue_id).first()
        movies = Movie.query.join(movie_venue).filter_by(
                    venue_id=venue_id).order_by(movie_venue.create_date.desc()).all()
        current_movies = []
        for movie in movies:
            mv_object= movie_venue.query.filter_by(movie_id=movie.movie_id, venue_id=venue.venue_id).first()
            mvtime=datetime.datetime.strptime(mv_object.time, '%d:%m:%Y %H:%M:%S')
            if mvtime > current_time:
                current_movies.append((movie, mv_object))
        return render_template('venue_details.html', venue_id=venue_id, movies=current_movies, venue=venue, user=user)
    return redirect('/user_login')

# User logout. if user presses back, the page won't be cached as the session has been killed.
@app.route("/user_logout")
def user_logout():
    flash('User logged out successfully')
    session.pop('user')
    response = make_response(redirect('/'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Book tickets functionality for a particular user in a venue for a particular movie.
@app.route('/book_tickets/<user_id>/<venue_id>/<movie_id>', methods=["GET", "POST"])
def book_tickets(user_id, venue_id, movie_id):
    if 'user' in session:
        user = User.query.filter_by(user_id=user_id).first()
        bookings = user.bookings
        # retrieve the Venue and Movie objects using the ids
        venue = Venue.query.get(venue_id)
        movie = Movie.query.get(movie_id)
        mv_obj=movie_venue.query.filter_by(movie_id=movie_id, venue_id=venue_id).first()
        mv = movie_venue.query.filter_by(
            movie_id=movie_id, venue_id=venue_id).first()
        price = mv.price
        num_of_tickets = 1
        if request.method == 'POST':
            if 'calc' in request.form:
                num_of_tickets = int(request.form.get("num_of_tickets"))
                price = mv.price
                return render_template('book_tickets.html', movie=movie, venue=venue, price=price, num_of_tickets=num_of_tickets, bookings=bookings, user_id=user_id, user=user, mv_obj=mv_obj)
            elif 'proceed' in request.form:
                if datetime.datetime.strptime(mv_obj.time, '%d:%m:%Y %H:%M:%S') <= datetime.datetime.now():
                    flash('This show has elapsed. You cannot buy tickets now')
                    return redirect(url_for('user_dashboardd', user_id=user_id))
                else:
                    num_of_tickets = int(request.form.get("num_of_tickets"))
                    price = mv.price
                    pricee = num_of_tickets*price
                    available_seats = mv.seats_available
                    if num_of_tickets > available_seats:
                        flash(
                            "Sorry, there are not enough seats available. Please choose a lower number of tickets.")
                        return redirect(url_for('book_tickets', user_id=user_id, venue_id=venue_id, movie_id=movie_id, movie=movie, venue=venue, price=price, num_of_tickets=num_of_tickets,bookings=bookings,user=user, mv_obj=mv_obj))
                    if num_of_tickets == 0:
                        flash('Please tell us the number of tickets you want to book!')
                        return redirect(url_for('book_tickets', user_id=user_id, venue_id=venue_id, movie_id=movie_id, venue=venue, price=price, num_of_tickets=num_of_tickets,bookings=bookings,user=user, mv_obj=mv_obj))
                    booking = Booking(movie_id=movie_id,venue_id=venue_id, user_id=user_id,
                                      num_of_tickets=num_of_tickets, create_date=datetime.datetime.now(), price=pricee)
                    db.session.add(booking)
                    db.session.commit()
                    mv.seats_available = available_seats - num_of_tickets
                    db.session.add(mv)
                    db.session.commit()
                    user = User.query.filter_by(user_id=user_id).first()
                    bookings = user.user_bookings

                    return redirect(url_for('display_bookings', user_id=user_id))
        return render_template('book_tickets.html', mv_obj=mv_obj,movie=movie, venue=venue, price=price, num_of_tickets=num_of_tickets, user=user, user_id=user_id)
    return redirect('/user_login')


@app.route('/bookings/<user_id>')
def display_bookings(user_id):
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()
        # bookings = user.user_bookings
        latest_bookings = Booking.query.filter_by(
            user_id=user_id).order_by(Booking.create_date.desc()).all()
        current_time=datetime.datetime.now()
        present_bookings=[]
        past_bookings=[]
        for booking in latest_bookings:
            if datetime.datetime.strptime(booking.movie_venue.time, '%d:%m:%Y %H:%M:%S') > current_time:
                present_bookings.append(booking)
            else:
                past_bookings.append(booking)
        return render_template('bookings.html', past_bookings=past_bookings,bookings=present_bookings, user=user, user_id=user_id, current_time=current_time)
    return redirect('user_login')

# allowing the user to cancel booking only when the showtime is greater than or equal to the present and disallow if the time has already elapsed.
@app.route('/cancel_booking/<user_id>/<booking_id>', methods=['GET', 'POST'])
def cancel_booking(user_id, booking_id):
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()
        # retrieve the Venue and Movie objects using the ids
        booking = Booking.query.get(booking_id)
        mv = movie_venue.query.filter_by(
            movie_id=booking.movie_id, venue_id=booking.venue_id).first()
        # if showtime.date_time < datetime.datetime.now():
        #     flash("Sorry, the showtime has already elapsed. You cannot delete this booking.")
        # else:
        mv.seats_available += booking.num_of_tickets
        db.session.add(mv)
        db.session.commit()
        db.session.delete(booking)
        db.session.commit()
        flash("Booking deleted successfully.")
        return redirect(url_for('display_bookings', user_id=user.user_id))
    return redirect(url_for('user_login', user_id=user_id, user=user))

#Display of venue popularity chart using matplotlib that gives a bar chart of which venue is the most popular based on the number of movies present.    
@app.route('/venues_popularity-chart')
def venues_popularity_chart():
    if "admin" in session and session["admin"] == params["admin_username"]:
        movie_venue_alias = aliased(movie_venue)

        # Query for the first chart
        venues = db.session.query(Venue, db.func.count(movie_venue_alias.movie_id)).join(movie_venue_alias, Venue.venue_id == movie_venue_alias.venue_id).group_by(Venue).all()
        venues_sorted = sorted(venues, key=lambda x: x[1], reverse=True)
        venue_names = [v[0].name for v in venues_sorted]
        movie_counts = [v[1] for v in venues_sorted]

        # Create the first chart
        plt.figure(figsize=(8, 6))
        plt.bar(venue_names, movie_counts)
        plt.xlabel('Venue')
        plt.ylabel('Number of movies')
        plt.title('Most popular venues for movies')
        plt.xticks(rotation=90)
        plt.tight_layout()

        # Save first chart to file
        chart_filename1 = "./static/popularity_chart1.png"
        plt.savefig(chart_filename1)

        # Query for the second chart
        bookings = db.session.query(Venue.name, db.func.count(Booking.booking_id)).join(Booking, Venue.venue_id == Booking.venue_id).group_by(Venue.name).all()
        bookings_sorted = sorted(bookings, key=lambda x: x[1], reverse=True)
        booking_venue_names = [b[0] for b in bookings_sorted]
        booking_counts = [b[1] for b in bookings_sorted]

        # Create the second chart
        plt.figure(figsize=(8, 6))
        plt.bar(booking_venue_names, booking_counts)
        plt.xlabel('Venue')
        plt.ylabel('Number of bookings')
        plt.title('Most popular venues for bookings')
        plt.xticks(rotation=90)
        plt.subplots_adjust(bottom=0.15, left=0.1, top=0.9, right=0.95)
        plt.tight_layout()

        # Save second chart to file
        chart_filename2 = "./static/popularity_chart2.png"
        plt.savefig(chart_filename2)

        # Return both charts as a template
        return render_template('popularity_chart.html', chart_filename1=chart_filename1, chart_filename2=chart_filename2)

    return redirect(url_for('admin_login'))

@app.route('/hello/<user_name>')
def tryingtasks(user_name):
    job=tasks.say_hello.delay(user_name)
    # result=job.wait()
    # return str(result),200
    return {
        'TASK_ID': job.id,
        'state': job.state,
        'result':job.result
    }

@app.route('/generate_csv/<venue_id>')
def tryingtasks2(venue_id):
    job=tasks.generate_csv.delay(venue_id)
    # result=job.wait()
    # return str(result),200
    return {
        'task_id': job.id,
        'state': job.state,
        'result':job.result
    }
@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    result = celery.AsyncResult(task_id)
    if result.state == 'PENDING':
        response = {
            'status': 'PENDING',
            'message': 'Task is still running.'
        }
    elif result.state == 'SUCCESS':
        response = {
            'status': 'SUCCESS',
            'message': 'Task has been completed successfully.',
            'result': result.get()  # You can also include the task result in the response
        }
    else:
        response = {
            'status': 'FAILURE',
            'message': 'Task execution failed.'
        }
    return jsonify(response), 200


@app.route('/download-file')
def download_file():
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    # Construct the full path to the 'data.csv' file inside the 'static' folder
    staticpath =os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../', 'static'))
    csv_file_path = os.path.join(staticpath, 'data.csv')
    return send_file(csv_file_path)

# @app.route('/helowwww')
# def tryingtasks3():
#     job=tasks.printtime.apply_async(countdown=10)
#     result=job.wait()
#     return str(result),200


@app.route('/show_updates', methods=['GET'])
def show_updates():
    return render_template('show_updates.html', error=None)

@app.route('/test_send_message', methods=['GET', 'POST'])
def test_send_message():
    sse.publish({'message':'hello'}, type='greeting')
    return 'Message sent'



@app.route('/test_send_message_vue', methods=['GET', 'POST'])
def test_send_message_vue():
    sse.publish({'message':'hello'}, type='greeting')
    return {'message' :'Success'}, 200

@app.route('/start_long_running_job', methods=['POST', 'GET'])
def start_long_running_job():
    job_id=tasks.long_running_job.delay()
    sse.publish({'message': 'starting job' + str(job_id)}, type='greeting')
    return 'STARTED' +str(job_id)