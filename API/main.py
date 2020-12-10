from flask import Flask,render_template,request,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, pre_load
from flask_api import FlaskAPI
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask_mail import *  
from random import *

app = FlaskAPI(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db'
db=SQLAlchemy(app)

mail = Mail(app)  
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465      
app.config["MAIL_USERNAME"] = ''  
app.config['MAIL_PASSWORD'] = ''  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  

mail = Mail(app)  

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True, unique=True)
    Email=db.Column(db.String(30), nullable=False)
    Password=db.Column(db.String(50), nullable=False)
    FirstName=db.Column(db.String(50), nullable=False)
    LastName=db.Column(db.String(50), nullable=False)
    Gender=db.Column(db.String(10), nullable=False)
    Profession=db.Column(db.String(50), nullable=False)
    Role=db.Column(db.String(50), nullable=False)
    Contact=db.Column(db.Integer, nullable=False)
    CompanyName=db.Column(db.String(50), nullable=False)
    CompanyPassword=db.Column(db.String(50), nullable=False)
    datePosted=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return 'User ' + str(self.id)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    Email=fields.Str()
    Password=fields.Str()
    FirstName=fields.Str()
    LastName=fields.Str()
    Gender=fields.Str()
    Profession=fields.Str()
    Role=fields.Str()
    Contact=fields.Int()
    datePosted=fields.DateTime(dump_only=True)
    CompanyName=fields.Str()
    CompanyPassword=fields.Str()
    Name = fields.Method("format_name", dump_only=True)

    def format_name(self, author):
        return "{}, {}".format(author.FirstName, author.LastName)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route("/")
def func():
    return render_template('home.html')

@app.route("/user/signup1",methods=['POST'])
def signup1():
    if request.method=="POST":
        Email=request.form['email']
        Password=request.form['password']
        fName=request.form['fName']
        lName=request.form['lName']
        Gender=request.form['gender']
        Profession=request.form['profession']
        Role=request.form['role']
        Contact=request.form['contact']
        post=User(Email=Email, Password=Password, FirstName=fName, LastName=lName, Gender=Gender, Profession=Profession, Role=Role, Contact=Contact, CompanyName='Aditya', CompanyPassword='Aditya')
        db.session.add(post)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return "User Added"
    else:
        return "Invalid request"

json = FlaskJSON(app)
@app.route("/user/signup/<name>",methods=['POST'])
def signup(name):
    data = request.get_json(force=True)
    try:
        Email=data['email']
        Password=data['password']
        fName=data['fName']
        lName=data['lName']
        Gender=data['gender']
        Profession=data['profession']
        Role=data['role']
        Contact=int(data['contact'])
        CompanyPassword=data['company_password']
        CompanyName=name
        post=User(Email=Email, Password=Password, FirstName=fName, LastName=lName, Gender=Gender, Profession=Profession, Role=Role, Contact=Contact, CompanyName=CompanyName, CompanyPassword=CompanyPassword)
        db.session.add(post)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value/ Email already registered')
    return json_response(Email=Email, FirstName=fName, LastName=lName, Gender=Gender, Profession=Profession, Role=Role, Contact=Contact, CompanyName=CompanyName)

@app.route("/user/all/<name>/<password>",methods=['GET','POST'])
def allusers(name,password):
    users=User.query.filter_by(CompanyName=name, CompanyPassword=password)
    result=users_schema.dump(users)
    return json_response(Users=result)

@app.route("/user/login1",methods=['POST'])
def login1():
    if request.method=="POST":
        Email=request.form['email']
        Password=request.form['password']
        post=User.query.filter_by(Email=Email, Password=Password).first()
        try:
            ID=post.id
            return "Login Success"
        except:
            return "Login Failed"
    else:
        return "Invalid request"

@app.route("/user/login",methods=['POST'])
def login():
    data = request.get_json(force=True)
    try:
        Email=data['email']
        Password=data['password']
        post=User.query.filter_by(Email=Email, Password=Password).first()
        try:
            ID=post.id
            return json_response(Email=Email)
        except:
            pass
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value')
    return json_response(status=400)

@app.route("/user/EmailVerification1",methods=['POST'])
def emailVerify1():
    email = request.form["email"]   
    return otpSend("email verification: ",email)

@app.route("/user/EmailVerification/<message>",methods=['POST'])
def emailVerify(message):
    data = request.get_json(force=True)
    try:
        Email=data['email']
        otp=otpSend(message,Email)
        return json_response(status=200, OTP=otp)
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value')
    return json_response(status=400)

def otpSend(message,email):
    otp = randint(000000,999999)
    msg = Message('OTP',sender = '', recipients = [email])  
    msg.body = 'OTP for ' + str(message) + ' is: ' + str(otp)  
    mail.send(msg) 
    return str(otp)