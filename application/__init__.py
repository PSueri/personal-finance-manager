import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

secret_key = os.environ.get("SECRET_KEY")

if not secret_key:
    raise RuntimeError(
        "La variabile d'ambiente SECRET_KEY non è configurata."
    )

app.config["SECRET_KEY"] = secret_key
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///Transazioni.db'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

from application import routes