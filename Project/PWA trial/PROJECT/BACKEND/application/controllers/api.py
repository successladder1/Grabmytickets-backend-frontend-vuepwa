import base64
from operator import or_
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask import Response
from matplotlib import pyplot as plt
from application.data.database import db
from application.data.models import Venue, Movie, movie_venue , Booking, User
from application.utils.validation import NotFoundError, ValidationError
import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource, Api
import json
from application.data import cached_functions
# from restapp import cache
from time import perf_counter_ns
from sqlalchemy.orm import aliased
output_fields={"venue_id": fields.Integer,
               "name":fields.String,"address":fields.String,"city":fields.String,"state":fields.String,"country":fields.String,"capacity": fields.Integer,"phone":fields.String,"email":fields.String}
create_venue_parser=reqparse.RequestParser()
create_venue_parser.add_argument('name')
create_venue_parser.add_argument('address')
create_venue_parser.add_argument('city')
create_venue_parser.add_argument('state')
create_venue_parser.add_argument('country')
create_venue_parser.add_argument('capacity')
create_venue_parser.add_argument('phone')
create_venue_parser.add_argument('email')



update_venue_parser=reqparse.RequestParser()
update_venue_parser.add_argument('name')
update_venue_parser.add_argument('address')
update_venue_parser.add_argument('city')
update_venue_parser.add_argument('state')
update_venue_parser.add_argument('country')
update_venue_parser.add_argument('capacity')
update_venue_parser.add_argument('phone')
update_venue_parser.add_argument('email')
class VenueAPI(Resource):
    @marshal_with(output_fields)
    @jwt_required()
    def get(self, venue_id):
        # Get the venue from database based on venue_id
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
            print("VenueAPI GET Method")
            venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
            # Format the json and return
            if venue:
                # return a valid venue_movie_dashboard
                return venue
            else:
                #return 404 error not found
                return {'message':'Venue Not found'},404
        else:
            return {'message': 'Only admin can access'}, 403
                # raise NotFoundError(status_code=404)

    @marshal_with(output_fields)   
    def put(self,venue_id):
        args=create_venue_parser.parse_args()
        name=args.get('name', None)
        address=args.get('address', None)
        city=args.get('city', None)
        state=args.get('state', None)
        country=args.get('country', None)
        capacity=args.get('capacity', None)
        phone=args.get('phone', None)
        email=args.get('email', None)
        venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
        if venue is None:
            raise NotFoundError(status_code=404)
        venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
        try: 
            int(capacity)
        except:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid capacity")
        if "@" in email:
            pass
        else:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid venue email")
        if name is None:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="venue name is required")
        venue.name=name
        venue.address=address
        venue.city=city
        venue.state=state
        venue.country=country
        # venue.date=date
        venue.capacity=capacity
        venue.phone=phone
        venue.email=email
        db.session.commit()
        return venue
    
    def delete(self,venue_id):
        venue=Venue.query.filter_by(venue_id=venue_id).first()
        if not venue:
            raise ValidationError(status_code=400, error_code="BE1002", error_message="Invalid venue_id")
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
        return "", 200
    
    def post(self):
        args=create_venue_parser.parse_args()
        name=args.get('name', None)
        address=args.get('address', None)
        city=args.get('city', None)
        state=args.get('state', None)
        country=args.get('country', None)
        capacity=args.get('capacity', None)
        phone=args.get('phone', None)
        email=args.get('email', None)
        if name is None:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="venue name is required")
        if "@" in email:
            pass
        else:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid venue email")
        try: 
            int(capacity)
        except:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid capacity")
        new_venue=Venue(name=name,address=address,city=city,state=state,country=country, capacity=capacity, phone=phone,email=email)
        db.session.add(new_venue)
        db.session.commit()
        return "",201
    
output_movie_fields={"movie_id": fields.Integer,
               "title":fields.String,"genre":fields.String,"language":fields.String,"runtime":fields.String,"rating":fields.String,"director": fields.String,
               "synopsis":fields.String,"release_date":fields.String,"trailer_url":fields.String}

output_movie_venue_fields = {
    "movie_id": fields.Integer,
    "venue_id": fields.Integer,
    "price": fields.Float,
    "date": fields.String,
    "time": fields.String,
    "create_date": fields.String,
    "seats_available": fields.Integer
}
create_movie_venue_parser = reqparse.RequestParser()
create_movie_venue_parser.add_argument('price')
create_movie_venue_parser.add_argument('date')
create_movie_venue_parser.add_argument('time')
create_movie_venue_parser.add_argument('seats_available')

create_movie_parser=reqparse.RequestParser()
create_movie_parser.add_argument('title')
create_movie_parser.add_argument('genre')
create_movie_parser.add_argument('language')
create_movie_parser.add_argument('runtime')
create_movie_parser.add_argument('rating')
create_movie_parser.add_argument('director')
create_movie_parser.add_argument('synopsis')
create_movie_parser.add_argument('release_date')
create_movie_parser.add_argument('trailer_url')


update_movie_parser=reqparse.RequestParser()
update_movie_parser.add_argument('title')
update_movie_parser.add_argument('genre')
update_movie_parser.add_argument('language')
update_movie_parser.add_argument('runtime')
update_movie_parser.add_argument('rating')
update_movie_parser.add_argument('director')
update_movie_parser.add_argument('synopsis')
update_movie_parser.add_argument('release_date')
update_movie_parser.add_argument('trailer_url')


class MovieAPI(Resource):
    @jwt_required()
    def get(self, venue_id,movie_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
        # Get the movie from database based on movie_id and venue_id
            print("MovieAPI GET Method")
            venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
            movie_venue_obj = db.session.query(movie_venue).filter(movie_venue.venue_id==venue_id, movie_venue.movie_id==movie_id).first()
            movie_idd=movie_venue_obj.movie_id
            movie=db.session.query(Movie).filter(Movie.movie_id==movie_idd).first()
            # Format the json and return
            if movie:
                # return a valid venue_movie_dashboard
                print(movie)
                result_dict = {
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
                    "venue_id": movie_venue_obj.venue_id,
                    "price": movie_venue_obj.price,
                    "date": movie_venue_obj.date,
                    "time": movie_venue_obj.time,
                    "create_date": movie_venue_obj.create_date,
                    "seats_available": movie_venue_obj.seats_available
                }
                return result_dict
            else:
                #return 404 error not found
                raise NotFoundError(status_code=404)
        else:
            return {'message': 'Only for admins'}, 403
    
    def put(self,venue_id,movie_id):
        args=create_movie_parser.parse_args()
        ARGSs=create_movie_venue_parser.parse_args()
        title=args.get('title', None)
        genre=args.get('genre', None)
        language=args.get('language', None)
        runtime=args.get('runtime', None)
        rating=args.get('rating', None)
        director=args.get('director', None)
        synopsis=args.get('synopsis', None)
        release_date=args.get('release_date', None)
        trailer_url=args.get('trailer_url', None)
        price = ARGSs.get('price', None)
        seats_available = ARGSs.get('seats_available', None)
        date = ARGSs.get('date', None)
        time = ARGSs.get('time', None)
        create_date = datetime.datetime.now()
        venue = Venue.query.get(venue_id)
        if not venue:
            raise ValidationError(status_code=400, error_code="BE1002", error_message="Invalid venue_id")
        if title is None:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="movie name is required")
        if "." in trailer_url:
            pass
        else:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid trailer url")
        try:
            datetime.datetime.strptime(time, '%d:%m:%Y %H:%M:%S')
        except:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid time format")
        try:
            int(price)
        except:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Price should be an integer")
        try:
            int(seats_available)
        except:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="seats_available should be an integer")
        movie_venue_obj = db.session.query(movie_venue).filter(movie_venue.venue_id==venue_id, movie_venue.movie_id==movie_id).first()
        movie_idd=movie_venue_obj.movie_id
        movie=db.session.query(Movie).filter(Movie.movie_id==movie_idd).first()
        if movie is None:
            raise NotFoundError(status_code=404)
        movie.title=title
        movie_venue_obj.price=price
        movie_venue_obj.date=date
        movie_venue_obj.time=time
        movie_venue_obj.seats_available=seats_available
        movie_venue_obj.create_date=create_date
        movie.title=title
        movie.genre=genre
        movie.language=language
        movie.runtime=runtime
        movie.rating=rating
        # venue.date=date
        movie.director=director
        movie.synopsis=synopsis
        movie.release_date=release_date
        movie.trailer_url=trailer_url
        db.session.commit()
        db.session.flush()
        db.session.commit()
        result_dict = {
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
                "venue_id": movie_venue_obj.venue_id,
                "price": movie_venue_obj.price,
                "date": movie_venue_obj.date,
                "time": movie_venue_obj.time,
                "create_date": movie_venue_obj.create_date,
                "seats_available": movie_venue_obj.seats_available
            }
        return result_dict
    
    def delete(self,venue_id, movie_id):
        
        bookings = db.session.query(Booking).filter(venue_id==venue_id, movie_id==movie_id).all()
        # bookings = Booking.query.filter_by(
        #     venue_id=venue_id, movie_id=movie_id).all()
        if bookings:
            for booking in bookings:
                db.session.delete(booking)
                db.session.commit()
        movie_venue_obj = db.session.query(movie_venue).filter(movie_venue.venue_id==venue_id, movie_venue.movie_id==movie_id).first()
        if movie_venue_obj:
            movie_obj = Movie.query.filter_by(movie_id=movie_venue_obj.movie_id).first()
            db.session.delete(movie_venue_obj)
            db.session.delete(movie_obj)
            db.session.commit()
            return "",200
        else:
            raise ValidationError(status_code=400, error_code="BE1002", error_message="Invalid venue_id or movie_id")

    def post(self, venue_id):
        args=create_movie_parser.parse_args()
        ARGSs=create_movie_venue_parser.parse_args()
        title=args.get('title', None)
        genre=args.get('genre', None)
        language=args.get('language', None)
        runtime=args.get('runtime', None)
        rating=args.get('rating', None)
        director=args.get('director', None)
        synopsis=args.get('synopsis', None)
        release_date=args.get('release_date', None)
        trailer_url=args.get('trailer_url', None)
        price = ARGSs.get('price', None)
        seats_available = ARGSs.get('seats_available', None)
        date = ARGSs.get('date', None)
        time = ARGSs.get('time', None)
        create_date = datetime.datetime.now()
        venue = Venue.query.get(venue_id)
        if not venue:
            raise ValidationError(status_code=400, error_code="BE1002", error_message="Invalid venue_id")
        if title is None :
            raise ValidationError(status_code=400,error_code="BE1001",error_message="movie name is required")
        if "." in trailer_url:
            pass
        else:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid trailer url")
        try:
            datetime.datetime.strptime(time, '%d:%m:%Y %H:%M:%S')
        except:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid time format")
        try:
            int(price)
        except:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="Price should be an integer")
        try:
            int(seats_available)
        except:
            raise ValidationError(status_code=400,error_code="BE1001",error_message="seats_available should be an integer")
        new_movie=Movie(title=title,genre=genre,language=language,runtime=runtime,rating=rating, director=director, synopsis=synopsis,release_date=release_date,trailer_url=trailer_url)
        db.session.add(new_movie)
        db.session.flush()
        mv = movie_venue(movie_id=new_movie.movie_id, venue_id=venue_id, price=price, date=date, time=time, create_date=create_date, seats_available=seats_available)
        db.session.add(mv)
        db.session.commit()
        return "",201



create_user_parser=reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('email')
create_user_parser.add_argument('password')

class AdminloginAPI(Resource):
    def get(self):
        return{"hello":"hi"}
    def post(self):
        data = create_user_parser.parse_args()
        username = data.get('username')
        password = data.get('password')
        email=data.get('email')
        print(username)
        print(data)
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            access_token = create_access_token(identity=username, additional_claims={'is_admin': user.is_admin, 'user_id': user.user_id, 'email': user.email, 'username':user.username})
            return {'access_token': access_token, 'isadmin': user.is_admin}, 200 
           
            # return {'yay': 'well-done'},200
        else:
            return {'message': 'Invalid credentials'}, 401
class AdminDashboardAPI(Resource):
    @jwt_required()
    # @role_required('admin')
    def get(self):

        # Check if the user is an admin
        current_user = get_jwt_identity()
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
            # Fetch data from the database
            # search_query = request.args.get('search', default='', type=str)
            # if search_query:
            #     venues = Venue.query.filter(or_(Venue.name.ilike(f"%{search_query}%"), Venue.city.ilike(f"%{search_query}%"))).all()
            # else:
            venues = Venue.query.all()
            # Convert venues to a list of dictionaries
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
            return {'venues_data': venues_data} ,201
        else:
             return {'message': 'Unauthorized'}, 403

class UserRegisterAPI(Resource):
    def get(self):
        return{"hello":"hi"}
    def post(self):
        data = create_user_parser.parse_args()
        username = data.get('username')
        password = data.get('password')
        email=data.get('email')
        print(username)
        print(data)
        user = User.query.filter_by(username=username).first()
        if user:
            return {'message': 'User already exists'}, 401
        else:
            user = User(username=username, password=password, email=email)
            db.session.add(user)
            db.session.commit()
            return {'message': 'Successfully registered'}, 200
    

class VenueMovieDashboard(Resource):
    @jwt_required()
    def get(self, venue_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
            venue = Venue.query.filter_by(venue_id=venue_id).first()
            if not venue:
                return {'message': 'Invalid venue_id'}
            movie_venue_data=[]
            movie_venue_objs = movie_venue.query.filter_by(venue_id=venue_id).all()
            for movie_venue_obj in movie_venue_objs:

                movie_idd=movie_venue_obj.movie_id
                movie=db.session.query(Movie).filter(Movie.movie_id==movie_idd).first()
            # Format the json and return
                if movie:
                # return a valid venue_movie_dashboard
                    print(movie)
                    result_dict = {
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
                        "venue_id": movie_venue_obj.venue_id,
                        "price": movie_venue_obj.price,
                        "date": movie_venue_obj.date,
                        "time": movie_venue_obj.time,
                        "create_date": movie_venue_obj.create_date,
                        "seats_available": movie_venue_obj.seats_available
                    }
                    movie_venue_data.append(result_dict)
            return {'movie_venue_data': movie_venue_data}
        else:
            return {'message': 'Only admins can access'} ,403
class Editvenueapi(Resource):
    def get(self,venue_id):
        return {'message':'hi'}
    @jwt_required()
    def post(self, venue_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
            args=create_venue_parser.parse_args()
            name=args.get('name')
            address=args.get('address')
            city=args.get('city')
            state=args.get('state')
            country=args.get('country')
            capacity=args.get('capacity')
            phone=args.get('phone')
            email=args.get('email')
            if venue_id == "0":
                # if name is None:
                #     raise ValidationError(status_code=400,error_code="BE1001",error_message="venue name is required")
                # if "@" in email:
                #     pass
                # else:
                #     raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid venue email")
                # try: 
                #     int(capacity)
                # except:
                #     raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid capacity")

                new_venue=Venue(name=name,address=address,city=city,state=state,country=country, capacity=capacity, phone=phone,email=email)
                db.session.add(new_venue)
                db.session.commit()
                return {'message':'Successfully added'},201
            else:
                venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
                if venue is None:
                    return {'message':'Venue Not found'} 
                # venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
                # try: 
                #     int(capacity)
                # except:
                #     raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid capacity")
                # if "@" in email:
                #     pass
                # else:
                #     raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid venue email")
                # if name is None:
                #     raise ValidationError(status_code=400,error_code="BE1001",error_message="venue name is required")
                venue.name=name
                venue.address=address
                venue.city=city
                venue.state=state
                venue.country=country
                # venue.date=date
                venue.capacity=capacity
                venue.phone=phone
                venue.email=email
                db.session.commit()
                return {'message':'Successfully edited'} , 201
        else:
            return {'message' :'Only admins can access.'} ,  403
class Editmovieapi(Resource):
    @jwt_required()
    def post(self, venue_id, movie_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
            args=create_movie_parser.parse_args()
            ARGSs=create_movie_venue_parser.parse_args()
            title=args.get('title', None)
            genre=args.get('genre', None)
            language=args.get('language', None)
            runtime=args.get('runtime', None)
            rating=args.get('rating', None)
            director=args.get('director', None)
            synopsis=args.get('synopsis', None)
            release_date=args.get('release_date', None)
            trailer_url=args.get('trailer_url', None)
            price = ARGSs.get('price', None)
            seats_available = ARGSs.get('seats_available', None)
            date = ARGSs.get('date', None)
            time = ARGSs.get('time', None)
            create_date = datetime.datetime.now()
            venue = Venue.query.get(venue_id)
            if not venue:
                return {'message': 'Venue not found'}
            if movie_id =="0":
            # if title is None :
            #     raise ValidationError(status_code=400,error_code="BE1001",error_message="movie name is required")
            # if "." in trailer_url:
            #     pass
            # else:
            #     raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid trailer url")
            # try:
            #     datetime.datetime.strptime(time, '%d:%m:%Y %H:%M:%S')
            # except:
            #     raise ValidationError(status_code=400,error_code="BE1001",error_message="Invalid time format")
            # try:
            #     int(price)
            # except:
            #     raise ValidationError(status_code=400,error_code="BE1001",error_message="Price should be an integer")
            # try:
            #     int(seats_available)
            # except:
            #     raise ValidationError(status_code=400,error_code="BE1001",error_message="seats_available should be an integer")
                new_movie=Movie(title=title,genre=genre,language=language,runtime=runtime,rating=rating, director=director, synopsis=synopsis,release_date=release_date,trailer_url=trailer_url)
                db.session.add(new_movie)
                db.session.flush()
                if venue_id != "0":
                    venue = Venue.query.filter_by(venue_id=venue_id).first()
                    mv = movie_venue(movie_id=new_movie.movie_id, venue_id=venue_id, price=price, date=date, time=time, create_date=create_date, seats_available=seats_available)
                    db.session.add(mv)
                    db.session.commit()
                    return {'message': 'Successfully Created'},201
            else:
                movie_venue_obj = db.session.query(movie_venue).filter(movie_venue.venue_id==venue_id, movie_venue.movie_id==movie_id).first()
                movie_idd=movie_venue_obj.movie_id
                movie=db.session.query(Movie).filter(Movie.movie_id==movie_idd).first()
                if movie is None:
                    return {'message':'movie not found'}
                movie.title=title
                movie_venue_obj.price=price
                movie_venue_obj.date=date
                movie_venue_obj.time=time
                movie_venue_obj.seats_available=seats_available
                movie_venue_obj.create_date=create_date
                movie.title=title
                movie.genre=genre
                movie.language=language
                movie.runtime=runtime
                movie.rating=rating
                movie.director=director
                movie.synopsis=synopsis
                movie.release_date=release_date
                movie.trailer_url=trailer_url
                db.session.commit()
                db.session.flush()
                db.session.commit()
            return {'message': 'Successfully updated'} , 201
        else:
            return {'message' :'Only admins can access'}, 403

class DeleteMovieAPI(Resource):
    @jwt_required()
    def delete(self,venue_id,movie_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
            movie_venue_obj = db.session.query(movie_venue).filter(movie_venue.venue_id==venue_id, movie_venue.movie_id==movie_id).first()
            bookings = db.session.query(Booking).filter(venue_id==venue_id, movie_id==movie_id).all()
            if bookings:
                for booking in bookings:
                    db.session.delete(booking)
                    db.session.commit()
            if movie_venue_obj:
                movie_obj = Movie.query.filter_by(movie_id=movie_venue_obj.movie_id).first()
                db.session.delete(movie_venue_obj)
                db.session.delete(movie_obj)
                db.session.commit()
                return {'message': 'Successfully deleted'},200
            else:
                return {'message': 'Movie does not exist'} , 401
        else:
            return {'message':'Only admins can access'} , 403
class DeleteVenueAPI(Resource):  
    @jwt_required()      
    def delete(self,venue_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
            venue=Venue.query.filter_by(venue_id=venue_id).first()
            if not venue:
                raise ValidationError(status_code=400, error_code="BE1002", error_message="Invalid venue_id")
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
            return "", 200
        else:
            return {'message' :'Only admins can access'} , 403

class UserDashboardAPI(Resource):
    @jwt_required()  # Require JWT authentication for this endpoint
    def get(self, user_id, category):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        print(loggedinuser.user_id)
        print(user_id)
        if (int(loggedinuser.user_id) == int(user_id)) and (loggedinuser.is_admin == 0):
    #     movies_by_venue = {}
    #     current_time = datetime.datetime.now()
    #     venues = Venue.query.all()
    #     for venue in venues:
    #         movies = Movie.query.join(movie_venue).filter_by(
    #             venue_id=venue.venue_id).order_by(movie_venue.time.asc()).all()
    #         current_movies = []
    #         for movie in movies:
    #             mv_object= movie_venue.query.filter_by(movie_id=movie.movie_id, venue_id=venue.venue_id).first()
    #             mvtime=datetime.datetime.strptime(mv_object.time, '%d:%m:%Y %H:%M:%S')
    #             if mvtime > current_time:
    #                 current_movies.append({
    #                     "movie_id": movie.movie_id,
    #                     "title": movie.title,
    #                     "genre": movie.genre,
    #                     "language": movie.language,
    #                     "runtime": movie.runtime,
    #                     "rating": movie.rating,
    #                     "director": movie.director,
    #                     "synopsis": movie.synopsis,
    #                     "release_date": movie.release_date,
    #                     "trailer_url": movie.trailer_url,
    #                     "venue_id": mv_object.venue_id,
    #                     "price": mv_object.price,
    #                     "date": mv_object.date,
    #                     "time": mv_object.time,
    #                     "create_date": mv_object.create_date,
    #                     "seats_available": mv_object.seats_available
    #                 })
    #         if current_movies:
    #             movies_by_venue[venue.venue_id] = current_movies
    #     venues_data = []
    #     for venue in venues:
    #         venues_data.append({
    #             'name': venue.name,
    #             'address': venue.address,
    #             'city': venue.city,
    #             'state': venue.state,
    #             'country': venue.country,
    #             'capacity': venue.capacity,
    #             'phone': venue.phone,
    #             'email': venue.email,
    #             'venue_id':venue.venue_id
    #             # Add other attributes as needed
    #         })
    #     print(venues_data)
    #     return {"movies_by_venue": movies_by_venue, "venues_data" :venues_data, 'category':'default'}, 200 
            start=perf_counter_ns()
            result_dict= cached_functions.getuserdashboardapi()
            stop=perf_counter_ns()
            print('timetaken',stop-start)
            print(result_dict)
            return result_dict, 200
        else:
            return {'message' :'You are not allowed to access this page'}, 403
class SearchUserAPI(Resource):
    @jwt_required()
    def get(self,user_id,category,query):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        print(loggedinuser.user_id)
        print(user_id)
        if (int(loggedinuser.user_id) == int(user_id)) and (loggedinuser.is_admin == 0):
        
            print(category)
            if category == 'venue' or query =='':
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
                return {"movies_by_venue": movies_by_venue, "venues_data" :venues_data, 'category':'venue', 'query':query}, 200  # Return the user dashboard data as a JSON response
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
                            temp =mv.movie
                            jsformmovie = {
                                "movie_id": temp.movie_id,
                                "title": temp.title,
                                "genre": temp.genre,
                                "language": temp.language,
                                "runtime": temp.runtime,
                                "rating": temp.rating,
                                "director": temp.director,
                                "synopsis": temp.synopsis,
                                "release_date": temp.release_date,
                                "trailer_url": temp.trailer_url,
                                "venue_id": mv.venue_id,
                                "price": mv.price,
                                "date": mv.date,
                                "time": mv.time,
                                "create_date": mv.create_date,
                                "seats_available": mv.seats_available
                            }
                            movies[movie_id] = {
                                'movie': jsformmovie,
                                'venues': []
                            }
                        tempv=mv.venue
                        jsformvenue = {
                            'name': tempv.name,
                            'address': tempv.address,
                            'city': tempv.city,
                            'state': tempv.state,
                            'country': tempv.country,
                            'capacity': tempv.capacity,
                            'phone': tempv.phone,
                            'email': tempv.email,
                            'venue_id':tempv.venue_id
                        }
                        movies[movie_id]['venues'].append(jsformvenue)


                print(f"results: {movies}")
                return {'movies':movies, 'query':query,category:'movie'} , 200
        else:
            return {'message' : 'You cannot access this page'}
    # def json_serializer(self, obj):
    #     if isinstance(obj, datetime.datetime):
    #         return obj.isoformat()
    #     return None
create_booking_parser = reqparse.RequestParser()
create_booking_parser.add_argument('price')
create_booking_parser.add_argument('date')
create_booking_parser.add_argument('time')
create_booking_parser.add_argument('seats_available')  
create_booking_parser.add_argument('venue_id') 
create_booking_parser.add_argument('movie_id') 
create_booking_parser.add_argument('user_id') 
create_booking_parser.add_argument('num_of_tickets')   
create_booking_parser.add_argument('create_date')   
create_booking_parser.add_argument('price')   

import datetime
from flask import jsonify
from flask_restful import Resource

# Assume the 'Booking' model is defined

class BookingAPI(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        print(loggedinuser.user_id)
        print(user_id)
        if (int(loggedinuser.user_id) == int(user_id)) and (loggedinuser.is_admin == 0):
        # latest_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.create_date.desc()).all()
        # current_time = datetime.datetime.now()
        # present_bookings = []
        # past_bookings = []
        # for booking in latest_bookings:
        #     movie_id=booking.movie_id
        #     venue_id=booking.venue_id
        #     venue = Venue.query.get(venue_id)
        #     movie = Movie.query.get(movie_id)
        #     mv = movie_venue.query.filter_by(
        #     movie_id=movie_id, venue_id=venue_id).first()
        #     result_dict = {
        #         'price': booking.price,
        #         'venue_id': booking.venue_id,
        #         'movie_id': booking.movie_id,
        #         'user_id': booking.user_id,
        #         'num_of_tickets': booking.num_of_tickets,
        #         'create_date': booking.create_date,
        #         'venue_name': venue.name,
        #         'movie_name': movie.title,
        #         'available_seats':mv.seats_available,
        #         'showtime': mv.time,
        #         'booking_id':booking.booking_id
                
        #     }
        #     if datetime.datetime.strptime(booking.movie_venue.time, '%d:%m:%Y %H:%M:%S') > current_time:
        #         present_bookings.append(result_dict)
        #     else:
        #         past_bookings.append(result_dict)
        
        # # Construct the JSON response
        # response = {
        #     'present_bookings': present_bookings,
        #     'past_bookings': past_bookings
        # }
            start=perf_counter_ns()
            response = cached_functions.getbookingofuser(user_id)
            stop=perf_counter_ns()
            print('timetaken',stop-start)
            return response,200
        else:
            return {'message': 'You cannot access this.'}, 403
    @jwt_required()
    def post(self_id,user_id,venue_id,movie_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        print(loggedinuser.user_id)
        print(user_id)
        if (int(loggedinuser.user_id) == int(user_id)) and (loggedinuser.is_admin == 0):
            data=create_booking_parser.parse_args()
            seats_available=data.get('seats_available')
            num_of_tickets=data.get('num_of_tickets')
            print(num_of_tickets)
            # user = User.query.filter_by(user_id=user_id).first()
            # bookings = user.bookings
            # venue = Venue.query.get(venue_id)
            # movie = Movie.query.get(movie_id)
            # mv_obj=movie_venue.query.filter_by(movie_id=movie_id, venue_id=venue_id).first()
            # mv = movie_venue.query.filter_by(
            #     movie_id=movie_id, venue_id=venue_id).first()
            # price = mv.price
            # num_of_tickets=int(num_of_tickets)
            # pricee = num_of_tickets*price
            # available_seats = mv.seats_available
            # if num_of_tickets > available_seats:
            #     return {'message':'Not enough seats available'},401
            # if num_of_tickets <= 0 or not num_of_tickets:
            #     return {'message':'Please tell us the number of tickets you want to book.'},401
            # booking = Booking(movie_id=movie_id,venue_id=venue_id, user_id=user_id,
            #                               num_of_tickets=num_of_tickets, create_date=datetime.datetime.now(), price=pricee)
            # db.session.add(booking)
            # db.session.commit()
            # mv.seats_available = available_seats - num_of_tickets
            # db.session.add(mv)
            # db.session.commit()
            response=cached_functions.postbooking(user_id,venue_id,movie_id, num_of_tickets)
            if (response['iden'] == '404'):
                print(response['message'])
                return response, 401
            if (response['iden'] == '200'):
                return response, 200
        else:
            return {'message' :'You cannot access this page.'}, 403
        
        # return response, 200
        # return {'message':'Successfully booked'},200
    @jwt_required()
    def delete(self, user_id,booking_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        print(loggedinuser.user_id)
        print(user_id)
        if (int(loggedinuser.user_id) == int(user_id)) and (loggedinuser.is_admin == 0):
        # user = User.query.filter_by(user_id=user_id).first()
        # # retrieve the Venue and Movie objects using the ids
        # booking = Booking.query.filter_by(user_id=user_id, booking_id=booking_id).first()
        # if not booking:
        #     return {'message': 'Booking not found'}, 404
        # mv = movie_venue.query.filter_by(
        #     movie_id=booking.movie_id, venue_id=booking.venue_id).first()
        # mv.seats_available += booking.num_of_tickets
        # db.session.add(mv)
        # db.session.commit()
        # db.session.delete(booking)
        # db.session.commit()
        # return {'message':'successfully deleted'}, 200
            response=cached_functions.deleteuserbooking(user_id,booking_id)
            if (response['iden'] == '404'):
                return response, 404
            if (response['iden'] == '200'):
                return response, 200
        else:
            return {'message' :'You cannot access this page.'},  403
         
class GetmovievenueuserAPI(Resource):
    @jwt_required()
    def get(self, user_id,venue_id,movie_id):
        # Get the movie from database based on movie_id and venue_id
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        print(loggedinuser.user_id)
        print(user_id)
        if (int(loggedinuser.user_id) == int(user_id)) and (loggedinuser.is_admin == 0):
            print("MovieAPI GET Method")
            venue=db.session.query(Venue).filter(Venue.venue_id==venue_id).first()
            movie_venue_obj = db.session.query(movie_venue).filter(movie_venue.venue_id==venue_id, movie_venue.movie_id==movie_id).first()
            # if (movie_venue_obj):
            #     return {}, 404
            movie_idd=movie_venue_obj.movie_id
            movie=db.session.query(Movie).filter(Movie.movie_id==movie_idd).first()
            # Format the json and return
            if movie:
                # return a valid venue_movie_dashboard
                print(movie)
                result_dict = {
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
                    "venue_id": movie_venue_obj.venue_id,
                    "price": movie_venue_obj.price,
                    "date": movie_venue_obj.date,
                    "time": movie_venue_obj.time,
                    "create_date": movie_venue_obj.create_date,
                    "seats_available": movie_venue_obj.seats_available,
                    'name': venue.name,
                    'address': venue.address,
                    'city': venue.city,
                    'state': venue.state,
                    'country': venue.country,
                    'capacity': venue.capacity,
                    'phone': venue.phone,
                    'email': venue.email,
                    'venue_id':venue.venue_id
                }
                return result_dict
            else:
                #return 404 error not found
                raise NotFoundError(status_code=404)
        else:
            return {'message': 'You cannot access this page.'}, 403
        
class GetvenuedetailsAPI(Resource):
    @jwt_required()
    def get(self, user_id, venue_id):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        print(loggedinuser.user_id)
        print(user_id)
        if (int(loggedinuser.user_id) == int(user_id)) and (loggedinuser.is_admin == 0):
            current_time = datetime.datetime.now()
            user = User.query.filter_by(user_id=user_id).first()
            venue=Venue.query.filter_by(venue_id=venue_id).first()
            vdic={
                    'name': venue.name,
                    'address': venue.address,
                    'city': venue.city,
                    'state': venue.state,
                    'country': venue.country,
                    'capacity': venue.capacity,
                    'phone': venue.phone,
                    'email': venue.email,
                    'venue_id':venue.venue_id
            }
            movies = Movie.query.join(movie_venue).filter_by(
                        venue_id=venue_id).order_by(movie_venue.create_date.desc()).all()
            current_movies = []
            if movies:
                for movie in movies:
                    mv_object= movie_venue.query.filter_by(movie_id=movie.movie_id, venue_id=venue.venue_id).first()
                    mvtime=datetime.datetime.strptime(mv_object.time, '%d:%m:%Y %H:%M:%S')
                    if mvtime > current_time:
                        mdic={"movie_id": movie.movie_id,
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
                        }
                        current_movies.append(mdic)
                return {"venue_id":venue_id, "movies":current_movies, "venue":vdic}, 200
            else:
                return 400
        else:
            return {'message': 'You cannot access this page.'},403
        
class GetpopularityAPI(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        if loggedinuser and loggedinuser.is_admin == 1:
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
            chart_data2 = {
                "labels": booking_venue_names,
                "counts": booking_counts,
                "title": "Most popular venues for bookings"
            }
            with open(chart_filename1, "rb") as chart1_file:
                chart1_data = base64.b64encode(chart1_file.read()).decode('utf-8')

            with open(chart_filename2, "rb") as chart2_file:
                chart2_data = base64.b64encode(chart2_file.read()).decode('utf-8')

            return jsonify({
                "chart1": chart1_data,
                "chart2": chart2_data
            })
        else:
            return {'message' :'Only admin can access this page.'}
        
class ReportoptionhandlerAPI(Resource):
    @jwt_required()
    def get(self, user_id, reportoption):
        current_user = get_jwt_identity()
        print(current_user)
        loggedinuser=User.query.filter_by(username = current_user).first()
        print(loggedinuser.user_id)
        print(user_id)
        if (int(loggedinuser.user_id) == int(user_id)) and (loggedinuser.is_admin == 0):
            print(reportoption)
            if reportoption == 'HTML':

                loggedinuser.is_html = True
                db.session.add(loggedinuser)
                db.session.commit()
            else:
                loggedinuser.is_html = False
                db.session.add(loggedinuser)
                db.session.commit()
            return {'message': 'Successfully saved'}, 200
        else:
            return {'message': 'You cannot access this page.'},403