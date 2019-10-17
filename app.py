from flask import Flask, jsonify, request
from models import User, user_schema, users_schema
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    app.run(debug=True)