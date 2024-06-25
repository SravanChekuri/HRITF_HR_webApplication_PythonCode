from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app
from flask_mail import Mail
from sqlalchemy import create_engine, Column, String
import os
from flask_bcrypt import Bcrypt
import smtplib
from flask_session import Session

 

# app.secret_key = 'os.urandom(24)'
app.secret_key = 'test'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:durga@localhost/nfcs10'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sample11nhr5@gmail.com'
app.config['MAIL_PASSWORD'] = 'dzvo yxnb iftp sgaq'
db = SQLAlchemy(app)
migrate=Migrate(app, db)
mail = Mail(app)
bcrypt = Bcrypt(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


