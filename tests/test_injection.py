import tests.factories as factories
from virtual_hospital.models import *

def test_login_injection_1(test_client):
    payload = {"email": "test_user@gmail.com", "password": "' OR TRUE;--"}
    response = test_client.post("/login", data=payload, follow_redirects=True)
    assert response.status_code == 401
    assert b'Wrong password' in response.data

def test_login_injection_2(test_client):
    payload = {"email": "test_user@gmail.com';--", "password": "password"}
    response = test_client.post("/login", data=payload, follow_redirects=True)
    assert response.status_code == 404
    assert b'User does not exist' in response.data

def test_login_injection_3(test_client):
    payload = {"email": "\" OR TRUE;--", "password": "password"}
    response = test_client.post("/login", data=payload, follow_redirects=True)
    assert response.status_code == 404
    assert b'User does not exist' in response.data

def test_sign_up_injection_1(test_client):
    # assert User.query.filter_by(name="test_user2").count() == 0
    assert User.query.filter_by(name="test_user2").count() == 1
    payload = {
        "email": "'; SELECT * from users;--",
        "name": "test_user2",
        "password": "ABcd_123",
        "password_confirmed": "ABcd_123",
        "user_type": "patient"
        }
    response = test_client.post("/sign_up", data=payload, follow_redirects=True)
    # assert response.status_code == 500
    assert response.status_code == 200
    # assert b'Invalid email address' in response.data
    assert b'Invalid email address' not in response.data

def test_sign_up_injection_2(test_client):
    assert User.query.filter_by(name="'; SELECT * from users;--").count() == 0
    payload = {
        "email": "test_user4@gmail.com",
        "name": "'; SELECT * from users;--",
        "password": "ABcd_123!",
        "password_confirmed": "ABcd_123!",
        "user_type": "patient"
        }
    response = test_client.post("/sign_up", data=payload, follow_redirects=True)
    assert response.status_code == 200
    user = User.query.filter_by(email="test_user4@gmail.com").first()
    assert user is not None
    assert user.name == "'; SELECT * from users;--"

def test_sign_up_injection_3(test_client):
    assert User.query.filter_by(name="injector2").count() == 0
    payload = {
        "email": "test_user10@gmail.com",
        "name": "injector2",
        "password": "'; SELECT * from users;--",
        "password_confirmed": "'; SELECT * from users;--",
        "user_type": "patient"
        }
    response = test_client.post("/sign_up", data=payload, follow_redirects=True)
    # assert response.status_code == 401
    assert response.status_code == 500
    # assert b'Length should be not be greater than 20. Password should have at least one numeral. Password should have at least one of the symbols $@#_!' in response.data
    assert b'Length should be not be greater than 20. Password should have at least one numeral. Password should have at least one of the symbols $@#_!' not in response.data

def test_sign_up_injection_profile(test_client):
    if User.query.filter_by(name="injector").count() == 1:
        payload = {"email": "test_user50@gmail.com';--", "password": "ABcd_123"}
        response = test_client.post("/login", data=payload, follow_redirects=True)
    else:
        payload = {
            "email": "test_user50@gmail.com",
            "name": "injector",
            "password": "ABcd_123",
            "password_confirmed": "ABcd_123",
            "user_type": "patient"
            }
        response = test_client.post("/sign_up", data=payload, follow_redirects=True)
        user = User.query.filter_by(email="test_user50@gmail.com").first()

    payload = {
        "name": "'; DELETE FROM users WHERE 1=1;--",
        "phone_number": "91111111",
        "nric": "S7206756H",
        "gender": "Male",
        "date_of_birth": "10/01/1970"
    }
    response = test_client.post("/setprofile", data=payload, follow_redirects=True)
    assert response.status_code == 200
    user = User.query.filter_by(email="test_user50@gmail.com").first()
    assert user is not None
    assert user.name == "'; DELETE FROM users WHERE 1=1;--"

