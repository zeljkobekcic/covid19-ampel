from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = b'some really random key'
CORS(app)

from . import routes
