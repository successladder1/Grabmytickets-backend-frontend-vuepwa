from operator import and_, or_
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import datetime
from flask import Flask, abort, make_response, render_template, request, session, redirect, flash, url_for
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

@app.route('/webhook_receiver/github', methods=['POST'])
def mywebhook():
    content=request.json
    print(content)
    print(request.headers)
    return "OK", 200

