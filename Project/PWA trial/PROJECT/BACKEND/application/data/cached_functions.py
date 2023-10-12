from application.data.models import Venue, Movie, movie_venue , Booking, User
from application.data.ccache import cache
from application.data.database import db
import datetime

@cache.cached(timeout=50, key_prefix='getuserdashboardapi')
def getuserdashboardapi():
        movies_by_venue = {}
        current_time = datetime.datetime.now()
        venues = Venue.query.all()
        for venue in venues:
            movies = Movie.query.join(movie_venue).filter_by(
                venue_id=venue.venue_id).order_by(movie_venue.time.asc()).all()
            current_movies = []
            for movie in movies:
                mv_object= movie_venue.query.filter_by(movie_id=movie.movie_id, venue_id=venue.venue_id).first()
                mvtime=datetime.datetime.strptime(mv_object.time, '%d:%m:%Y %H:%M:%S')
                if mvtime > current_time:
                    current_movies.append({
                        "movie_id": movie.movie_id,
                        "title": movie.title,
                        "genre": movie.genre,
                        "language": movie.language,
                        "runtime": movie.runtime,
                        "rating": movie.rating,
                        "director": movie.director,
                        "synopsis": movie.synopsis,
                        "release_date": movie.release_date,
                        "trailer_url": movie.trailer_url,
                        "venue_id": mv_object.venue_id,
                        "price": mv_object.price,
                        "date": mv_object.date,
                        "time": mv_object.time,
                        "create_date": mv_object.create_date,
                        "seats_available": mv_object.seats_available
                    })
            if current_movies:
                movies_by_venue[venue.venue_id] = current_movies
        venues_data = []
        for venue in venues:
            venues_data.append({
                'name': venue.name,
                'address': venue.address,
                'city': venue.city,
                'state': venue.state,
                'country': venue.country,
                'capacity': venue.capacity,
                'phone': venue.phone,
                'email': venue.email,
                'venue_id':venue.venue_id
                # Add other attributes as needed
            })
        print(venues_data)
        return {"movies_by_venue": movies_by_venue, "venues_data" :venues_data, 'category':'default'}

@cache.memoize(50)
def getbookingofuser(user_id):
        latest_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.create_date.desc()).all()
        current_time = datetime.datetime.now()
        present_bookings = []
        past_bookings = []
        for booking in latest_bookings:
            movie_id=booking.movie_id
            venue_id=booking.venue_id
            venue = Venue.query.get(venue_id)
            movie = Movie.query.get(movie_id)
            mv = movie_venue.query.filter_by(
            movie_id=movie_id, venue_id=venue_id).first()
            result_dict = {
                'price': booking.price,
                'venue_id': booking.venue_id,
                'movie_id': booking.movie_id,
                'user_id': booking.user_id,
                'num_of_tickets': booking.num_of_tickets,
                'create_date': booking.create_date,
                'venue_name': venue.name,
                'movie_name': movie.title,
                'available_seats':mv.seats_available,
                'showtime': mv.time,
                'booking_id':booking.booking_id
                
            }
            if datetime.datetime.strptime(booking.movie_venue.time, '%d:%m:%Y %H:%M:%S') > current_time:
                present_bookings.append(result_dict)
            else:
                past_bookings.append(result_dict)
        
        # Construct the JSON response
        response = {
            'present_bookings': present_bookings,
            'past_bookings': past_bookings
        }
        return response

def postbooking(user_id,venue_id,movie_id, num_of_tickets):
    user = User.query.filter_by(user_id=user_id).first()
    bookings = user.bookings
    venue = Venue.query.get(venue_id)
    movie = Movie.query.get(movie_id)
    mv_obj=movie_venue.query.filter_by(movie_id=movie_id, venue_id=venue_id).first()
    mv = movie_venue.query.filter_by(
        movie_id=movie_id, venue_id=venue_id).first()
    price = mv.price
    num_of_tickets=int(num_of_tickets)
    pricee = num_of_tickets*price
    available_seats = mv.seats_available
    if num_of_tickets > available_seats:
        return {'message':'Not enough seats available', 'iden': '401'}
    if num_of_tickets <= 0 or not num_of_tickets:
        return {'message':'Please tell us the number of tickets you want to book.', 'iden':'401'}
    booking = Booking(movie_id=movie_id,venue_id=venue_id, user_id=user_id,
                                  num_of_tickets=num_of_tickets, create_date=datetime.datetime.now(), price=pricee)
    db.session.add(booking)
    db.session.commit()
    mv.seats_available = available_seats - num_of_tickets
    db.session.add(mv)
    db.session.commit()
    cache.delete_memoized(getbookingofuser, user_id)
    return {'message':'Successfully booked', 'iden': '200'}

def deleteuserbooking(user_id,booking_id):
        user = User.query.filter_by(user_id=user_id).first()
        # retrieve the Venue and Movie objects using the ids
        booking = Booking.query.filter_by(user_id=user_id, booking_id=booking_id).first()
        if not booking:
            return {'message': 'Booking not found', 'iden':'404'}
        mv = movie_venue.query.filter_by(
            movie_id=booking.movie_id, venue_id=booking.venue_id).first()
        mv.seats_available += booking.num_of_tickets
        db.session.add(mv)
        db.session.commit()
        db.session.delete(booking)
        db.session.commit()
        cache.delete_memoized(getbookingofuser, user_id)
        return {'message':'successfully deleted', 'iden': '200'}