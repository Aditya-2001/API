from flask import Flask,render_template,request,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, pre_load
from flask_api import FlaskAPI
from flask_json import FlaskJSON, JsonError, json_response, as_json

app = FlaskAPI(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db'
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True, unique=True)
    Email=db.Column(db.String(30), nullable=False)
    Password=db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return 'User ' + str(self.id)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    Email=fields.Str()
    Password=fields.Str()
    def format_name(self, author):
        return 'User ' + str(self.id)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route("/")
def func():
    return render_template('home.html')

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

json = FlaskJSON(app)
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