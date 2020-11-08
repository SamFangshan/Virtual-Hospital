import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_crontab import Crontab
from flask_login import LoginManager
from flask_session import Session

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

# User Tracking Control
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    from virtual_hospital.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'login'

crontab = Crontab(app)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

from virtual_hospital import views, commands, cronjobs
