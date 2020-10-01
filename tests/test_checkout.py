from virtual_hospital.models import *


def test_checkout_no_log_in(test_client):
    test_client.get("/logout", follow_redirects=True)

    # checkout
    response = test_client.post('/checkout', data={'amount': 10})
    assert 302 == response.status_code


def test_checkout_normal(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # checkout
    response = test_client.post('/checkout', data={'amount': 1023.12}, follow_redirects=True)
    assert b'102312' in response.data

    assert 200 == response.status_code
    test_client.get("/logout", follow_redirects=True)


def test_checkout_get(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # checkout
    response = test_client.get('/checkout', follow_redirects=True)

    assert 405 == response.status_code
    test_client.get("/logout", follow_redirects=True)