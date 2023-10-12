from application.data.database import db
# from flask_security import UserMixin, RoleMixin
import json
with open('config.json', 'r') as c:
    params = json.load(c)['params']

# role_users = db.Table('role_users',
#                       db.Column('user_id', db.Integer(), db.ForeignKey('user.user_id')),
#                       db.Column('role_id', db.Integer(), db.ForeignKey('role.role_id'))
#                       )
# class Role(db.Model, RoleMixin):
#     __tablename__ = "role"
#     role_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
class movie_venue(db.Model):
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.venue_id'), nullable=False, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey(
        'movie.movie_id'), nullable=False, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String, nullable=False)
    create_date = db.Column(db.Integer, nullable=False)
    seats_available = db.Column(db.Integer, nullable=False)
    venue = db.relationship(
        'Venue', backref=db.backref('venue_movies', lazy=True))
    movie = db.relationship(
        'Movie', backref=db.backref('venue_movies', lazy=True))


class Venue(db.Model):
    __tablename__ = "venue"
    venue_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)


class Movie(db.Model):
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.String(10), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.String(200), nullable=False)
    synopsis = db.Column(db.String(500), nullable=False)
    trailer_url = db.Column(db.String(500), nullable=False)


class Booking(db.Model):
    __tablename__ = "booking"
    booking_id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.venue_id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey(
        'movie.movie_id'), nullable=False)
    create_date = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    num_of_tickets = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
         'user.user_id'), nullable=False)
    venue = db.relationship(
        'Venue', backref=db.backref('bookings', lazy=True))
    movie = db.relationship(
        'Movie', backref=db.backref('bookings', lazy=True))
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    @property
    def movie_venue(self):
        return movie_venue.query.filter_by(movie_id=self.movie_id, venue_id=self.venue_id).first()



class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    user_bookings = db.relationship(
        'Booking', backref='user_bookings', lazy=True, overlaps="bookings,user")
    is_admin=db.Column(db.Boolean(), default=False)
    email = db.Column(db.String(200), nullable=False)
    is_html=db.Column(db.Boolean(), default=False)

