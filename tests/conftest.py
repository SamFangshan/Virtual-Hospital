import os
from dotenv import load_dotenv

# load environmental variables
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

import sqlalchemy
from flask import Flask

import pytest
from flask_sqlalchemy import SQLAlchemy
from pytest_postgresql.janitor import DatabaseJanitor
from virtual_hospital import app as _app
from virtual_hospital import db
from virtual_hospital.models import *
import tests.factories as factories


try:
    pg_user = os.environ['PG_USER']
    pg_password = os.environ['PG_PASSWORD']
    pg_host = os.environ['PG_HOST']
    pg_port = os.environ['PG_PORT']
    pg_database = os.environ['TEST_PG_DATABASE']
    DB_CONN = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
                                                            pg_user,
                                                            pg_password,
                                                            pg_host,
                                                            pg_port,
                                                            pg_database
                                                            )
except KeyError:
    raise KeyError('Test database connection config not found in the environment.')
else:
    DB_OPTS = sqlalchemy.engine.url.make_url(DB_CONN).translate_connect_args()

pytest_plugins = ['pytest-flask-sqlalchemy']


@pytest.fixture(scope='session')
def database(request):
    '''
    Create a Postgres database for the tests, and drop it when the tests are done.
    '''
    pg_host = DB_OPTS.get("host")
    pg_port = DB_OPTS.get("port")
    pg_user = DB_OPTS.get("username")
    pg_pass = DB_OPTS.get("password")
    pg_db = DB_OPTS["database"]

    db_janitor = DatabaseJanitor(pg_user, pg_host, pg_port, pg_db, 12, pg_pass)

    db_janitor.init()

    @request.addfinalizer
    def drop_database():
        db_janitor.drop()


@pytest.fixture(scope='session')
def app(database):
    '''
    Create a Flask app context for the tests.
    '''
    _app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI=DB_CONN
    )

    return _app

@pytest.fixture(scope='session')
def test_client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def _db(app):
    '''
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    '''
    db.create_all()
    init_db()

    return db

@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return "en_US"

def init_db():
    factories.TestUserFactory()

    factories.DoctorFactory.create_batch(3)
    # reset increment id sequence number
    db.engine.execute('ALTER SEQUENCE {}_{}_seq RESTART WITH {};'.format('user', 'id', 3 + 1))

    factories.PatientFactory.create_batch(2)
    # reset increment id sequence number
    # db.engine.execute('ALTER SEQUENCE {}_{}_seq RESTART WITH {};'.format('user', 'id', 3 + 2 + 1))

    factories.AppointmentTimeSlotFactory.create_batch(1)
    # reset increment id sequence number
    db.engine.execute('ALTER SEQUENCE {}_{}_seq RESTART WITH {};'.format('appointment_time_slot', 'id', 1 + 1))

    factories.PrescriptionFactoryForPayment()
    factories.AppointmentFactoryForPayment.create_batch(2)
    factories.PrescriptionFactoryPaid()
    db.engine.execute('ALTER SEQUENCE {}_{}_seq RESTART WITH {};'.format('prescription', 'id', 2 + 1))

    factories.DrugFactory.create_batch(3)
    db.engine.execute('ALTER SEQUENCE {}_{}_seq RESTART WITH {};'.format('drug', 'id', 3 + 1))

    factories.PrescriptionDrugFactory.create_batch(3)
    db.engine.execute('ALTER SEQUENCE {}_{}_seq RESTART WITH {};'.format('prescription_drug', 'id', 3 + 1))

