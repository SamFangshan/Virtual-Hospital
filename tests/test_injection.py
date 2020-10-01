import tests.factories as factories
from virtual_hospital.models import *

def test_login_injection_1(test_client):
    payload = {"email": "test_user@gmail.com", "password": "\" OR TRUE;--"}
    response = test_client.post("/login", data=payload, follow_redirects=True)
    assert response.status_code == 401
    assert b'Wrong password' in response.data

def test_login_injection_2(test_client):
    payload = {"email": "test_user@gmail.com\"--", "password": "password"}
    response = test_client.post("/login", data=payload, follow_redirects=True)
    assert response.status_code == 404
    assert b'User does not exist' in response.data

def test_login_injection_3(test_client):
    payload = {"email": "\" OR TRUE;--", "password": "password"}
    response = test_client.post("/login", data=payload, follow_redirects=True)
    assert response.status_code == 404
    assert b'User does not exist' in response.data

##def test_sign_up_success(test_client):
##    assert User.query.filter_by(name="test_user2").count() == 0
##    payload = {
##        "email": "test_user2@gmail.com",
##        "name": "test_user2",
##        "password": "ABcd_123",
##        "password_confirmed": "ABcd_123",
##        "user_type": "patient"
##        }
##    response = test_client.post("/sign_up", data=payload, follow_redirects=True)
##    assert response.status_code == 200
##    user = User.query.filter_by(email="test_user2@gmail.com").first()
##    assert user is not None
##    assert user.name == "test_user2"
##
##def test_sign_up_existing_email(test_client):
##    assert User.query.filter_by(name="test_user").count() == 1
##    existing_user = User.query.filter_by(name="test_user").first()
##    payload = {
##        "email": existing_user.email,
##        "name": "test_user2",
##        "password": "ABcd_123",
##        "password_confirmed": "ABcd_123",
##        "user_type": "patient"
##        }
##    response = test_client.post("/sign_up", data=payload, follow_redirects=True)
##    assert response.status_code == 500
##    assert b'Already Registered' in response.data
##
##def test_sign_up_incorrect_password(test_client):
##    # password does not meet requirements
##    payload = {
##        "email": "test_user3@gmail.com",
##        "name": "test_user3",
##        "password": "password",
##        "password_confirmed": "password",
##        "user_type": "patient"
##        }
##    response = test_client.post("/sign_up", data=payload, follow_redirects=True)
##    assert response.status_code == 500
##
##    # 2 passwords are different
##    payload = {
##        "email": "test_user3@gmail.com",
##        "name": "test_user3",
##        "password": "ABcd_123",
##        "password_confirmed": "ABcd_456",
##        "user_type": "patient"
##        }
##    response = test_client.post("/sign_up", data=payload, follow_redirects=True)
##    assert response.status_code == 500
##    print(response.data)
##    assert b'Please ensure that two password are the same.' in response.data

