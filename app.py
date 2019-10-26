from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:ge3k@localhost/terusan'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Product Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    passwd = db.Column(db.String(36))
    email = db.Column(db.Integer())
    telepon = db.Column(db.Integer(), nullable=True)
    saldo = db.Column(db.Integer(), nullable=True)
    activities = db.relationship('Activity', backref='owner')
    
    def __init__(self, username, passwd, email, telepon, saldo, activities):
        self.username = username
        self.passwd = passwd
        self.email = email
        self.telepon = telepon
        self.saldo = saldo
        self.activities = activities

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_name = db.Column(db.String(35))
    tipe = db.Column(db.String(6))
    date_time = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
    nominal = db.Column(db.Integer())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)

    def __init__(self, activity_name, tipe, date_time, nominal, owner):
        self.activity_name = activity_name
        self.tipe = tipe
        self.date_time = date_time
        self.nominal = nominal
        self.owner_id = owner_id

class Wahana(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wahana = db.Column(db.String(15))
    harga = db.Column(db.Integer())

# Product Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'passwd', 'email', 'telepon', 'saldo')

class ActivitySchema(ma.Schema):
    class Meta:
        fields = ('id', 'activity_name', 'tipe', 'date_time', 'nominal', 'owner')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
activity_schema = ActivitySchema()
activitys_schema = ActivitySchema(many=True)

# Create a User
@app.route('/daftar', methods=['POST'])
def add_user():
    username = request.json['username']
    passwd = request.json['passwd']
    email = request.json['email']
    telepon = request.json['telepon']
    saldo = request.json['saldo']
    
    new_user = User(username, passwd, email, telepon, saldo)
    
    db.session.add(new_user)
    db.session.commit()
    
    return user_schema.jsonify(new_user)

## Get user
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

## Login
@app.route('/login', methods=['POST'])
def login():
    iden = request.json['telp/email']
    passwd = request.json['passwd']
    
    user = User.query.filter_by(telepon=telepon).first()
    if iden == user.telepon or iden == user.email and passwd == user.passwd:
        return user_schema.jsonify(user)

## Scan
@app.route('/scan', methods=['POST'])
def scan():
    nama_w = request.json['wahana']
    user_id = request.json['id']

    wahana = Wahana.query.filter_by(wahana=nama_w).first()
    user = User.query.get(id)
    tipe = 'debet'
    date_time = datetime.now()
    nominal = wahana.harga

    new_act = Activity(nama_w,tipe,date_time,nominal,user.username)
    db.session.add(new_act)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)