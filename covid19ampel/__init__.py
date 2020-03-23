from flask import Flask
from flask_cors import CORS
from flask_dotenv import DotEnv

app = Flask(__name__)

try:
    env = DotEnv()
    env.init_app(app)
except Exception:
    pass

app.secret_key = b'some really random key'

CORS(app)

from . import routes
