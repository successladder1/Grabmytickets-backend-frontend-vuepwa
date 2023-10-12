from operator import and_, or_
import os
from application.jobs.workers import celery
from datetime import datetime, timedelta
from celery.schedules import crontab
import time
from json import dumps
from httplib2 import Http
from celery.result import AsyncResult
from flask_sse import sse
from application.data.models import *
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from jinja2 import Template
from weasyprint import HTML
# @celery.on_after_finalize.connect
# def setup_periodic_task(sender, **kwargs):
#     sender.add_periodic_task(10.0, printtime.s(), name='At every 10 seconds')

@celery.task()
def say_hello(name):
    print('inside task')
    time.sleep(10)
    print('hello', name)
    return 'hello '+ name

@celery.task()
def printtime():
    print('start')
    now=datetime.now()
    print('now in task', now)
    dt_string = now.strftime("%d/%m/%Y%H:%M:%S")
    sse.publish({'message':'STARTED IN printtime TASK =' + dt_string}, type='greeting')
    print('date and time: ', dt_string)
    print('complete')
    return dt_string

@celery.task()
def generate_csv(venue_id):
    import csv 
    # field names 
    current_time = datetime.now()
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
        rows=[]
        for movie in movies:
            mv_object= movie_venue.query.filter_by(movie_id=movie.movie_id, venue_id=venue.venue_id).first()
            mvtime=datetime.strptime(mv_object.time, '%d:%m:%Y %H:%M:%S')
            ro= [movie.movie_id,movie.title,movie.genre, movie.language,movie.runtime, movie.rating,movie.director, movie.synopsis,movie.release_date, movie.trailer_url, mv_object.price,mv_object.date , mv_object.time, mv_object.create_date,mv_object.seats_available   ]
            # if mvtime > current_time:
            bookings = Booking.query.filter_by(movie_id=movie.movie_id, venue_id=venue.venue_id).all()
            booked_seats = sum(booking.num_of_tickets for booking in bookings)
            ro=ro+ [booked_seats]
            rows.append(ro)
        

    fields = ['movie_id','Title', 'Genre', 'Language', 'runtime', 'rating','director', 'synopsis', 'release_date', 'trailer_url', 'price', 'date', 'timeofshow', 'create_date' ,'seats_available', 'number_of_bookings' ] 

    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../','../', 'static'))

    # Construct the full path to the 'data.csv' file inside the 'static' folder
    csv_file_path = os.path.join(static_folder, 'data.csv')
    # writing to csv file 
    with open(csv_file_path, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 

        # writing the fields 
        csvwriter.writerow(fields) 

        # writing the data rows 
        csvwriter.writerows(rows)
    
    return 'CSV generation successful'

@celery.task()
def long_running_job():
    print('started long running job')
    now=datetime.now()
    dt_string = now.strftime("%d/%m/%Y%H:%M:%S")
    sse.publish({'message':'STARTED IN TASK =' + dt_string}, type='greeting')
    for lp in range(10):
        
        # progress bar and emails
        print('running')
        dt_string = now.strftime("%d/%m/%Y%H:%M:%S")
        sse.publish({'message':'STARTED IN TASK =' + str(lp)}, type='greeting')
        time.sleep(2)
    now=datetime.now()
    dt_string = now.strftime("%d/%m/%Y%H:%M:%S")
    sse.publish({'message':'completed IN TASK =' + dt_string}, type='greeting')

@celery.task()
def googlechatwebhook():
    url="https://chat.googleapis.com/v1/spaces/AAAAh-UtaYA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=eKOI5rVI5DgVyy4FI8vaBFUc9dGQNneZf27Zo3HczK8"
    bot_message={'text':'hi'}
    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )
    print(response)
    return 'Reminder will be sent shortly'
# @celery.on_after_finalize.connect
# def setup_periodic_task(sender, **kwargs):
#     sender.add_periodic_task(10.0, googlechatwebhook.s(), name='At every 10 seconds')


def send_email(to_address, subject, message, content='text', attachment_file=None):
    SMTP_SERVER_HOST = "127.0.0.1"
    SMTP_SERVER_PORT = 1025
    SENDER_ADDRESS='email@somethin.com'
    SENDER_PASSWORD='somepass'
    msg=MIMEMultipart()
    msg['From'] = SENDER_ADDRESS
    msg['To']=to_address
    msg['Subject']=subject
    if content =='html':
         
    # create mimetext with the message in html and attach it to the message that will be sent in the email through smtp
        msg.attach(MIMEText(message, 'html'))
    else:
         msg.attach(MIMEText(message, 'plain'))
    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            part=MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",  f"attachment; filename ={attachment_file}")
        msg.attach(part)
    
    s=smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(SENDER_ADDRESS,SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    print("SMTP connection successful!")
    return True 
    print("SMTP connection failed:", e)
    return False
    # return True

@celery.task()
def send_reminder_via_email():
    current_time = datetime.now()

    # # Calculate the date and time 24 hours ago
    last_24_hours = current_time - timedelta(hours=24)
    # # Query the User table to get all users who made a booking in the last 24 hours
    users_without_bookings_last_24_hours = User.query.outerjoin(User.user_bookings).filter(or_(Booking.create_date == None, Booking.create_date < last_24_hours)).all()
    print(users_without_bookings_last_24_hours)
    for user in users_without_bookings_last_24_hours:
        print(user.email)
        sendto = user.email
        send_email(to_address=sendto, subject="Reminder to grab your ticket!!!",message= "How long will you not grab a showww? Comeon roll over to the exciting experience")
        print("sending email to ", sendto)
    return 'Emails will be sent shortly'

# @celery.on_after_finalize.connect
# def setup_daily_reminder_task(sender, **kwargs):
#     # Send reminder via email every day at 6:00 PM
#         sender.add_periodic_task(
#         crontab(hour=18, minute=0),  # 6:00 PM daily
#         send_reminder_via_email.s(),
#         name='send-reminder-email'
#         )

def format_message(template_file, data={}):
    current_date = datetime.now()

    # Calculate the date 30 days ago from the current date
    past_30_days = current_date - timedelta(days=30)

    # Get the bookings made in the past 30 days (replace `user_id` with the actual user ID)
    bookings = Booking.query.filter_by(user_id=data.user_id).filter(
        Booking.create_date >= past_30_days,
        Booking.create_date <= current_date
    ).all()

    # bookings=Booking.query.filter_by(user_id=data.user_id).all()
    print(bookings)
    with open(template_file) as file:
            template=Template(file.read())
            return template.render(data=data, bookings=bookings )    
@celery.task()
def send_monthly_report():
    users=User.query.all()
    for user in users:
        templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../", "../", "templates"))
        template_path = os.path.join(templates_dir, "reportmonthly.html")
        message= format_message(template_path, user)
        if user.is_html ==True:
            send_email(user.email, subject='Monthly Entertainment report', message=message, content='html')
        else:
            pdfrep=create_pdf_report(user)
            send_email(user.email, subject='Monthly Entertainment report', message=message, content='html', attachment_file=pdfrep)

# @celery.on_after_finalize.connect
# def setup_periodic_task(sender, **kwargs):
#     sender.add_periodic_task(20.0, send_monthly_report.s(), name='At every 10 seconds')

# @celery.on_after_finalize.connect
# def setup_monthly_report_task(sender, **kwargs):
#     # Send monthly report on the first day of every month at 6:00 AM
#     sender.add_periodic_task(
#         crontab(day_of_month='1', hour=6, minute=0),
#         send_monthly_report.s(),
#         name='send-monthly-report'
    # )
# @celery.on_after_finalize.connect
# def setup_periodic_task(sender, **kwargs):
#     sender.add_periodic_task(20.0, send_reminder_via_email.s(), name='At every 10 seconds')

def create_pdf_report( data):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../","../", "templates"))
    template_path = os.path.join(templates_dir, "reportmonthly.html")
    message= format_message(template_path, data=data)
    html=HTML(string=message)
    filename=str(data.username)+ '.pdf'
    html.write_pdf(target=filename)
    return filename