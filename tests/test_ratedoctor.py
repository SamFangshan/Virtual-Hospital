from virtual_hospital.models import *
import datetime


def test_ratedoctor_no_log_in(test_client):
    test_client.get("/logout", follow_redirects=True)

    response = test_client.get('/ratedoctor/appointment/1')
    assert 302 == response.status_code


def test_ratedoctor_normal(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # rate doctor
    response = test_client.get('/ratedoctor/appointment/1', follow_redirects=True)
    doctor_name = Doctor.query.get(1).name
    assert b'Anaesthesia' in response.data
    assert bytes(doctor_name, 'utf-8') in response.data
    assert bytes(datetime.datetime.today().date().strftime('%d/%m/%Y, %H:%M:%S'), 'utf-8') in response.data
    assert 200 == response.status_code

    response = test_client.post('/ratedoctor/appointment/1', data=dict(
            rate=4
        ), follow_redirects=True)
    assert 200 == response.status_code

    assert Appointment.query.get(1).rating == 4 # confirm rating correct

    response = test_client.get('/ratedoctor/appointment/1', follow_redirects=True)
    assert 404 == response.status_code # cannot rate a second time

    test_client.get("/logout", follow_redirects=True)


def test_ratedoctor_unauthorized_doctor(test_client):
    doctor = Doctor.query.get(1)
    email = doctor.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # payment
    response = test_client.get('/ratedoctor/appointment/1', follow_redirects=True)

    assert 403 == response.status_code
    test_client.get("/logout", follow_redirects=True)


def test_ratedoctor_unauthorized_patient(test_client):
    patient = Patient.query.get(102)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # payment
    response = test_client.get('/ratedoctor/appointment/1', follow_redirects=True)

    assert 403 == response.status_code
    test_client.get("/logout", follow_redirects=True)


def test_ratedoctor_non_existent(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # payment
    response = test_client.get('/ratedoctor/appointment/1024', follow_redirects=True)

    assert 404 == response.status_code
    test_client.get("/logout", follow_redirects=True)
