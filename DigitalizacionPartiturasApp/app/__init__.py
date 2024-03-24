from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'partituras2024ubu'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tu_base_de_datos.db'
db = SQLAlchemy(app)

from . import routes
