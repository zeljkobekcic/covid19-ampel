from flask import Flask
from flask_cors import CORS
from flask_dotenv import DotEnv
import os

app = Flask(__name__)
CORS(app)

if os.path.exists('.env'):
    env = DotEnv()
    env.init_app(app)


from . import routes
