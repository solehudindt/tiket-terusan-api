from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import text as sa_text
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
    username = db.Column(db.String(15), primary_key=True, unique=True)
    name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(40), unique=True)
    telepon = db.Column(db.String(13))
    saldo = db.Column(db.Integer(), default=0)
    auth = db.relationship('Auth', backref='user', uselist=False)
    activities = db.relationship('Activity', backref='owner')
    
    def __init__(self, username, name, email, telepon):
        self.username = username
        self.name = name
        self.email = email
        self.telepon = telepon

class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passwd = db.Column(db.String(100))
    # username = db.Column(db.String(15), db.ForeignKey('user.username'))
    user_id = db.Column(db.String(15), db.ForeignKey('user.username'))

    def __init__(self, passwd, user_id):
        self.passwd = passwd
        self.user_id = user_id

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_name = db.Column(db.String(35))
    tipe = db.Column(db.String(6))
    date_time = db.Column(db.DateTime, nullable=False, default=db.func.now())
    nominal = db.Column(db.Integer())
    owner_id = db.Column(db.String(15), db.ForeignKey('user.username'),
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
        fields = ('username', 'name', 'email', 'telepon', 'saldo')

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
    name = request.json['nama']
    passwd = request.json['passwd']
    email = request.json['email']
    telepon = request.json['telepon']

    try:
        new_user = User(username, name, email, telepon)
        new_auth = Auth(generate_password_hash(passwd), username)
            
        db.session.add(new_user)
        db.session.add(new_auth)
        db.session.commit()
    except:
        return jsonify({'error': 'An error occurred saving the user to the database'}), 500
    
    return jsonify({'status':'success'}), 200

## Login
@app.route('/login', methods=['POST'])
def login():

    iden = request.json['username']
    passwd = request.json['passwd']
    x = {"status":"email atau password salah"}
    
    auth = Auth.query.filter_by(user_id=iden).first()
    user = User.query.filter_by(username=iden).first()

    try:
        if iden == auth.user_id and check_password_hash(auth.passwd, passwd):
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
        if user.username:
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
        if user.saldo < whn.harga:
            x["status"] = "saldo tidak cukup"
            
        elif user.saldo != 0:        
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