from flask_sqlalchemy import SQLAlchemy, ENUM
from flask_marshmallow import Marshmallow
import os

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Product Class/Model
sexs = ('L', 'P')
sexs_enum = ENUM(*sexs, name='sex')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(25), unique=True)
    usia = db.Column(db.Integer(2))
    sex = db.Column(sexs_enum)
    saldo = db.Column(db.Float)
    harga_tiket = db.Column(db.Float)
    
    def __init__(self, nama, usia, sex, saldo, harga):
        self.nama = nama
        self.usia = usia
        self.sex = sex
        self.saldo = saldo
        self.harga_tiket = harga_tiket

# Product Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nama', 'usia', 'sex', 'saldo', 'harga_tiket')

# Init schema
user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)