from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from flask_cors import CORS
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
cors = CORS(app, resources={r"*": {"origins": "*"}})

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:ge3k@localhost/terusan'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
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
    email = db.Column(db.String(40), unique=True)
    telepon = db.Column(db.String(13), nullable=True)
    saldo = db.Column(db.Integer(), default=0)
    activities = db.relationship('Activity', backref='owner')
    
    def __init__(self, username, passwd, email, telepon):
        self.username = username
        self.passwd = passwd
        self.email = email
        self.telepon = telepon

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_name = db.Column(db.String(35))
    tipe = db.Column(db.String(6))
    date_time = db.Column(db.DateTime, nullable=False, default=db.func.now())
    nominal = db.Column(db.Integer())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)

    def __init__(self, activity_name, tipe, date_time, nominal, owner):
        self.activity_name = activity_name
        self.tipe = tipe
        self.date_time = date_time
        self.nominal = nominal
        self.owner = owner

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
        fields = ('id', 'activity_name', 'tipe', 'date_time', 'nominal')

## Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
activity_schema = ActivitySchema()
activitys_schema = ActivitySchema(many=True)

@app.route('/')
def index():
    x = {"status":"running"}
    return jsonify(x)

## Create a User
@app.route('/daftar', methods=['POST'])
def add_user():
    username = request.json['username']
    passwd = request.json['passwd']
    email = request.json['email']
    telepon = request.json['telepon']
    
    new_user = User(username, passwd, email, telepon)
    
    db.session.add(new_user)
    db.session.commit()
    
    return user_schema.jsonify(new_user)

## Login
@app.route('/login', methods=['POST'])
def login():

    iden = request.json['email']
    passwd = request.json['passwd']
    x = {"status":"email atau password salah"}
    
    user = User.query.filter_by(email=iden).first()

    try:
        if iden == user.email and passwd == user.passwd:
            return user_schema.jsonify(user)
        else:
            return jsonify(x)
    except(AttributeError):
        return jsonify(x)

## topup
@app.route('/topup', methods=['POST'])
def topup():
    username = request.json['username']
    nominal = request.json['nominal']
    x = {"status":""}
    user = User.query.filter_by(username=username).first()
    tipe = 'kredit'
    date = datetime.now()

    try:
        if user.id:
            new_act = Activity(activity_name="topup",tipe=tipe,date_time=date,nominal=nominal,owner=user)
            db.session.add(new_act)
            db.session.commit()

            user.saldo += nominal
            db.session.commit()
            x["status"] = "success"
    except(AttributeError):
        x["status"] = "username salah"

    return jsonify(x)

## Scan
@app.route('/scan', methods=['POST'])
def scan():
    nama_w = request.json['wahana']
    username = request.json['username']
    x = {"status":""}

    whn = Wahana.query.filter_by(wahana=nama_w).first()
    user = User.query.filter_by(username=username).first()
    try:
        if user.saldo != 0:        
            tipe = 'debet'
            date = datetime.now()
            nominal = whn.harga

            new_act = Activity(whn.wahana,tipe,date,nominal,user)
            db.session.add(new_act)
            db.session.commit()

            user.saldo -= nominal
            db.session.commit()

            x["status"] = "success"
        else:
            x["status"] = "saldo tidak cukup"
    except(AttributeError):
        x["status"] = "wahana atau username tidak terdaftar"

    return jsonify(x)

## Get user
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

## get history
@app.route('/history/<id>', methods=['GET'])
def get_history(id):
    user = User.query.get(id)

    try:
        act = []
        for i in (user.activities):
            x = {"activity_name":i.activity_name,
                "tipe":i.tipe,
                "date_time":i.date_time,
                "nominal":i.nominal
            }
            act.append(x)
        data = {"data":act}
        return jsonify(data)
    except(AttributeError):
        return jsonify({"status":"Activity kosong"})

if __name__ == '__main__':
    app.run(debug=True)