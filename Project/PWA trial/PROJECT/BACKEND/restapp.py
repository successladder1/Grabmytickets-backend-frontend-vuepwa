import json
from flask import Flask, abort, render_template, request, session, redirect, flash, url_for
from flask_restful import Api, Resource
import os
from flask_sqlalchemy import SQLAlchemy
from application.data.database import db
from flask_cors import CORS
# from flask_security import SQLAlchemyUserDatastore, login_required, roles_accepted, roles_required, SQLAlchemySessionUserDatastore, Security
from application.data.models import User
from application.jobs import workers
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_sse import sse
from admin_user import create_admin_user
# from flask_caching import Cache
cache=None
app=None
celery=None
def create_app():

    app=Flask(__name__, template_folder='templates')
    current_dir=os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///" + os.path.join(current_dir, "ticketshow.db")
    db.init_app(app)
    api=Api(app)
    
    with open('config.json','r') as c:
        params=json.load(c)['params']
    app.secret_key='super-secret-key'
    # app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
    # app.config['SECURITY_PASSWORD_SALT'] = 'somethingsecret'
    # app.config['SECURITY_REGISTERABLE'] = True
    # app.config['SECURITY_UNAUTHORIZED_VIEW'] = None
    # app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
    # app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'
    # user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    # security=Security(app, user_datastore)
    jwt = JWTManager(app)
    celery=workers.celery
    app.config['CELERY_BROKER_URL']='redis://localhost:6379/1'
    app.config['CELERY_BACKEND_URL']='redis://localhost:6379/2'
    celery.conf.update(
        broker_url = app.config['CELERY_BROKER_URL'],
        result_backend= app.config['CELERY_BACKEND_URL']
    )
    # app.config['CACHE_TYPE']='RedisCache'
    # app.config['CACHE_REDIS_HOST'] = 'localhost'
    # app.config['CACHE_REDIS_PORT'] = 6379
    app.config['REDIS_URL'] = 'redis://localhost:6379'
    CORS(app)
    celery.Task=workers.ContextTask
    app.app_context().push()
    # cache=Cache(app)
    if not app._got_first_request:
        with app.app_context():
            create_admin_user()
    app.app_context().push()
    # return app, api
    return app, api, celery
app, api, celery=create_app()
    # return app, api, celery, cache
# app, api, celery, cache=create_app()
# app,api=create_app()
# if not app._got_first_request:
#     with app.app_context():
#         create_admin_user()
app.register_blueprint(sse,url_prefix='/stream')
app.app_context().push()
from application.controllers.controllers import * 
from application.controllers.webhooks import * 
from application.controllers.api import VenueAPI,ReportoptionhandlerAPI, MovieAPI,GetpopularityAPI,GetvenuedetailsAPI,SearchUserAPI, AdminloginAPI,BookingAPI,GetmovievenueuserAPI,UserDashboardAPI, AdminDashboardAPI,DeleteMovieAPI,DeleteVenueAPI, UserRegisterAPI, VenueMovieDashboard,Editvenueapi,Editmovieapi
api.add_resource(VenueAPI,'/api/edit/0','/api/edit/<venue_id>')
api.add_resource(MovieAPI,'/api/edit_movie/<venue_id>/0','/api/edit_movie/<venue_id>/<movie_id>')
api.add_resource(AdminloginAPI, '/api/vueadmin_login')
api.add_resource(AdminDashboardAPI, '/api/vueadmin_dashboard')
api.add_resource(UserRegisterAPI, '/api/vueregister')
api.add_resource(VenueMovieDashboard, '/api/vuevenue_movie_dashboard/<venue_id>')
api.add_resource(Editvenueapi, '/api/vueeditvenue/<venue_id>')
api.add_resource(Editmovieapi, '/api/vueeditmovie/<venue_id>/<movie_id>')
api.add_resource(DeleteMovieAPI, '/api/vuedeletemovie/<venue_id>/<movie_id>')
api.add_resource(DeleteVenueAPI, '/api/vuedeletevenue/<venue_id>')
api.add_resource(UserDashboardAPI, '/api/vueuserdashboard/<user_id>/<category>')
api.add_resource(BookingAPI, '/api/vuebook/<user_id>/<venue_id>/<movie_id>', '/api/vuebook/<user_id>', '/api/vuebook/<user_id>/<booking_id>')
api.add_resource(GetmovievenueuserAPI, '/api/getmovievenueuser/<user_id>/<venue_id>/<movie_id>')
api.add_resource(SearchUserAPI, '/api/searchbyuser/<user_id>/<category>/<query>')
api.add_resource(GetvenuedetailsAPI, '/api/getvenuedetails/<user_id>/<venue_id>')
api.add_resource(GetpopularityAPI, '/api/vuegetpopularity')
api.add_resource(ReportoptionhandlerAPI, '/api/reportoptionhandler/<user_id>/<reportoption>')
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
if __name__=="__main__":
    app.run(debug=True)

