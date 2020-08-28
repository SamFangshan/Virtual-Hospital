import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

pg_user = os.getenv('PG_USER')
pg_password = os.getenv('PG_PASSWORD')
pg_host = os.getenv('PG_HOST')
pg_port = os.getenv('PG_PORT')
pg_database = os.getenv('PG_DATABASE')

sqlachemy_connection_str = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
                                                                pg_user,
                                                                pg_password,
                                                                pg_host,
                                                                pg_port,
                                                                pg_database
                                                                )

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = sqlachemy_connection_str
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from virtual_hospital import views, errors, commands
