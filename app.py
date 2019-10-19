from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
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
    nama = db.Column(db.String(25), unique=True)
    passwd = db.Column(db.String(36))
    usia = db.Column(db.Integer())

    def __init__(self, nama, passwd, usia):
        self.nama = nama
        self.passwd = passwd
        self.usia = usia

class Tiket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    harga = db.Column(db.Integer)
    saldo = db.Column(db.Integer)

    def __init__(self, harga, saldo):
        self.harga = harga
        self.saldo = saldo

# Product Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nama', 'passwd', 'usia')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Create a Product
@app.route('/daftar', methods=['POST'])
def add_product():
  nama = request.json['nama']
  passwd = request.json['passwd']
  usia = request.json['usia']

  new_user = User(nama, passwd, usia)

  db.session.add(new_user)
  db.session.commit()

  return user_schema.jsonify(new_user)

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

if __name__ == '__main__':
    app.run(debug=True)