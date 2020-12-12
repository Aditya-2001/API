from flask import Flask,render_template,request,redirect,jsonify,session,g
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
app.secret_key = 'akadbakadbabmbebosoomailagalulubyebye'

mail = Mail(app)  
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465      
app.config["MAIL_USERNAME"] = 'djangonotification@gmail.com'  
app.config['MAIL_PASSWORD'] = 'aditya.iiita0330'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  

mail = Mail(app)  

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        users=User.query.all()
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

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
    datePosted=db.Column(db.DateTime, nullable=False, default=datetime.now)
    authenticated = db.Column(db.Boolean, default=False)
    LastLogin = db.Column(db.String, nullable=False)
    LastLogout = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return 'User ' + str(self.id)
    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

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
    authenticated=fields.Bool()
    LastLogin=fields.Str()
    LastLogout=fields.Str()
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
        if duplicate(Email)==False:
            return "Email already registered"
        Password=request.form['password']
        fName=request.form['fName']
        lName=request.form['lName']
        Gender=request.form['gender']
        Profession=request.form['profession']
        Role=request.form['role']
        Contact=request.form['contact']
        now = datetime.now()
        date=now.strftime("%m/%d/%Y, %H:%M:%S")
        post=User(Email=Email, Password=Password, FirstName=fName, LastName=lName, Gender=Gender, Profession=Profession, Role=Role, Contact=Contact, LastLogin=date, LastLogout=date)
        db.session.add(post)
        CommitSession()
        return "User Added"
    else:
        return "Invalid request"

json = FlaskJSON(app)
@app.route("/user/signup",methods=['POST'])
def signup():
    data = request.get_json(force=True)
    try:
        Email=data['email']
        if duplicate(Email)==False:
            return json_response(description='Email already registered', status=400)
        Password=data['password']
        fName=data['fName']
        lName=data['lName']
        Gender=data['gender']
        Profession=data['profession']
        Role=data['role']
        Contact=int(data['contact'])
        now = datetime.now()
        date=now.strftime("%m/%d/%Y, %H:%M:%S")
        post=User(Email=Email, Password=Password, FirstName=fName, LastName=lName, Gender=Gender, Profession=Profession, Role=Role, Contact=Contact, LastLogin=date, LastLogout=date)
        db.session.add(post)
        CommitSession()
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value')
    return json_response(Email=Email, FirstName=fName, LastName=lName, Gender=Gender, Profession=Profession, Role=Role, Contact=Contact)

def duplicate(Email):
    post=User.query.filter_by(Email=Email).first()
    try:
        ID=post.id
        return False
    except:
        return True
    
def CommitSession():
    try:
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

@app.route("/user/all",methods=['GET','POST'])
def allusers():
    users=User.query.filter_by()
    for each in users:
        each.Password="Can't be displayed"
    result=users_schema.dump(users)
    return json_response(Users=result)


@app.route("/user/login1",methods=['POST'])
def login1():
    if request.method=="POST":
        session.pop('user_id', None)
        Email=request.form['email']
        Password=request.form['password']
        post=User.query.filter_by(Email=Email, Password=Password).first()
        try:
            ID=post.id
            now=datetime.now()
            date=now.strftime("%m/%d/%Y, %H:%M:%S")
            post.LastLogin=date
            if post.authenticated==True:
                post.LastLogout=date
            post.authenticated=True
            session['user_id'] = post.id
            db.session.add(post)
            CommitSession()
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
            now=datetime.now()
            date=now.strftime("%m/%d/%Y, %H:%M:%S")
            post.LastLogin=date
            if post.authenticated==True:
                post.LastLogout=date
            post.authenticated=True
            db.session.add(post)
            CommitSession()
            return json_response(Email=Email, Authenticated=True)
        except:
            pass
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value')
    return json_response(status=400)

@app.route("/user/logout1",methods=['POST','GET'])
def logout1():
    now=datetime.now()
    date=now.strftime("%m/%d/%Y, %H:%M:%S")
    if g.user == None:
        return json_response(status=400, Description="Already Logged out")
    user_id=g.user.id
    g.user.authenticated=False
    g.user.LastLogout=date
    db.session.add(g.user)
    try:
        db.session.commit()
        session.pop('user_id', None)
        return json_response(status=200, Authenticated=False)
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return json_response(status=400)

@app.route("/user/logout",methods=['POST','GET'])
def logout():
    data = request.get_json(force=True)
    try:
        Email=data['email']
        post=User.query.filter_by(Email=Email).first()
        try:
            ID=post.id
            if(post.authenticated):
                now=datetime.now()
                date=now.strftime("%m/%d/%Y, %H:%M:%S")
                post.LastLogout=date
            post.authenticated=False
            db.session.add(post)
            CommitSession()
            return json_response(status=200, Email=Email, Authenticated=False)
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
    msg = Message('OTP',sender = 'djangonotification@gmail.com', recipients = [email])  
    msg.body = 'OTP for ' + str(message) + ' is: ' + str(otp)  
    mail.send(msg) 
    return str(otp)

@app.route("/user/ForgotPassword1",methods=['POST'])
def resetPassword1():
    Email=request.form['email']
    NewPassword=request.form['new_password']
    post=User.query.filter_by(Email=Email).first()
    try:
        post.Password=NewPassword
        try:
            db.session.commit()
            return "Password Changed"
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return "ERROR"
    except:
        return "ERROR"

@app.route("/user/ForgotPassword",methods=['POST'])
def resetPassword():
    data = request.get_json(force=True)
    try:
        Email=data['email']
        NewPassword=data['new_password']
        post=User.query.filter_by(Email=Email).first()
        try:
            post.Password=NewPassword
            try:
                db.session.commit()
                return json_response(Email=Email)
            except:
                db.session.rollback()
            finally:
                db.session.close()
        except:
            pass
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value')
    return json_response(status=400)

@app.route("/user/profile1",methods=['POST'])
def profile1():
    Email=request.form['email']
    user=User.query.filter_by(Email=Email).first()
    try:
        id=user.id
        user.Password="Can't be displayed"
        result=user_schema.dump(user)
        return json_response(User=result)
    except:
        return "ERROR"

@app.route("/user/profile",methods=['POST'])
def profile():
    data = request.get_json(force=True)
    try:
        Email=data['email']
        user=User.query.filter_by(Email=Email).first()
        try:
            id=user.id
            user.Password="Can't be displayed"
            result=user_schema.dump(user)
            return json_response(User=result)
        except:
            pass
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value')
    return json_response(status=400)

@app.route("/user/updateprofile",methods=['POST'])
def updateprofile():
    data = request.get_json(force=True)
    try:
        Email=data['email']
        post=User.query.filter_by(Email=Email).first()
        try:
            ID=post.id
            post.FirstName=data['fName']
            post.LastName=data['lName']
            post.Gender=data['gender']
            post.Profession=data['profession']
            post.Role=data['role']
            post.Contact=int(data['contact'])
            db.session.add(post)
            CommitSession()
            user=User.query.filter_by(Email=Email).first()
            try:
                id=user.id
                user.Password="Can't be displayed"
                result=user_schema.dump(user)
                return json_response(User=result)
            except:
                pass
        except:
            pass
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value')
    return json_response(Email=Email, FirstName=fName, LastName=lName, Gender=Gender, Profession=Profession, Role=Role, Contact=Contact)