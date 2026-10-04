from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///Transazioni.db'
app.config['SECRET_KEY']='password1'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
#app.app_context().push()

from application import routes