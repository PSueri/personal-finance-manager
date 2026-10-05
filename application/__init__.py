import os

from flask import Flask

from application.extensions import db, csrf

app = Flask(__name__)

secret_key = os.environ.get("SECRET_KEY")

if not secret_key:
    raise RuntimeError(
        "La variabile d'ambiente SECRET_KEY non è configurata."
    )

app.config["SECRET_KEY"] = secret_key
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///Transazioni.db'

db.init_app(app)
csrf.init_app(app)

from application import routes