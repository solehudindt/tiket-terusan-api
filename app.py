from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://scott:root@localhost/terusan'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Product Class/Model

trans = db.Table('trans',
    db.Column('user_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('tiket_id', db.Integer, db.ForeignKey('page.id'), primary_key=True),
    tgl_trans = db.Column(db.Date),
    saldo = db.Column(db.Integer)
)

class Tiket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    harga = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(25), unique=True)
    passwd = db.Column(db.String(36))
    usia = db.Column(db.Integer())

    trans = db.relationship('Tiket', secondary=trans, lazy='subquery',
        backref=db.backref('pages', lazy=True))
    
    def __init__(self, nama, usia, passwd):
        self.nama = nama
        self.usia = usia
        self.passwd = passwd

# Product Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nama', 'usia', 'saldo', 'harga_tiket')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Create a Product
@app.route('/daftar', methods=['POST'])
def add_product():
  nama = request.json['nama']
  usia = request.json['usia']
  saldo = request.json['saldo']
  harga_tiket = request.json['harga_tiket']

  new_user = User(nama, usia, saldo, harga_tiket)

  db.session.add(new_user)
  db.session.commit()

  return user_schema.jsonify(new_user)

if __name__ == '__main__':
    app.run(debug=True)