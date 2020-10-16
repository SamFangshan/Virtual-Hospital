import tests.factories as factories
from virtual_hospital.models import *

def login(test_client):
    patient = Patient.query.get(10001)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

def test_change_settings_duplicate_email(test_client):
    login(test_client)

    test_user2 = User.query.filter_by(name="test_user2").first()
    response = test_client.post("/settings", data={'email': test_user2.email}, follow_redirects=True)
    assert b'Already Registered' in response.data

def test_change_settings_change_email_success(test_client):
    login(test_client)

    response = test_client.post("/settings", data={'email': 'random_email@gmail.com'}, follow_redirects=True)
    assert b'Settings updated' in response.data

def test_change_settings_change_password_failed(test_client):
    login(test_client)

    # 2 passwords are different
    response = test_client.post("/settings", data={'password': 'ABcd_123'}, follow_redirects=True)
    assert b'Please ensure that two password are the same' in response.data

    response = test_client.post("/settings", data={'password': 'ABcd_123', 'password_confirmed': '123'}, follow_redirects=True)
    assert b'Please ensure that two password are the same' in response.data

def test_change_settings_change_password_success(test_client):
    login(test_client)

    response = test_client.post("/settings", data={'password': 'ABcd_123', 'password_confirmed': 'ABcd_123'}, follow_redirects=True)
    assert b'Settings updated' in response.data
    