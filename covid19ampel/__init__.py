from flask import Flask
from flask_cors import CORS
from flask_dotenv import DotEnv

app = Flask(__name__)
CORS(app)

from . import routes
