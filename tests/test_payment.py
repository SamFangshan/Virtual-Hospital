from virtual_hospital.models import *


def test_payment_no_log_in(test_client):
    test_client.get("/logout", follow_redirects=True)

    response = test_client.get('/payment/prescription/1')
    assert 302 == response.status_code


def test_payment_normal(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # payment
    response = test_client.get('/payment/prescription/1', follow_redirects=True)
    assert b'Apomorphine' in response.data
    assert b'Cupric Sulfate' in response.data
    assert b'Ipecac' in response.data

    assert b'26' in response.data
    assert b'18.5' in response.data
    assert b'30.5' in response.data

    assert b'75' in response.data  # total

    assert 200 == response.status_code
    test_client.get("/logout", follow_redirects=True)


def test_payment_paid(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # payment
    response = test_client.get('/payment/prescription/2', follow_redirects=True)

    assert 404 == response.status_code
    test_client.get("/logout", follow_redirects=True)


def test_payment_unauthorized_doctor(test_client):
    doctor = Doctor.query.get(1)
    email = doctor.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # payment
    response = test_client.get('/payment/prescription/1', follow_redirects=True)

    assert 403 == response.status_code
    test_client.get("/logout", follow_redirects=True)


def test_payment_unauthorized_patient(test_client):
    patient = Patient.query.get(102)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # payment
    response = test_client.get('/payment/prescription/1', follow_redirects=True)

    assert 403 == response.status_code
    test_client.get("/logout", follow_redirects=True)


def test_payment_non_existent(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # payment
    response = test_client.get('/payment/prescription/1024', follow_redirects=True)

    assert 404 == response.status_code
    test_client.get("/logout", follow_redirects=True)