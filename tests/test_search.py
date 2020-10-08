from virtual_hospital.models import *

def test_search_found(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    existing_doctor = Doctor.query.get(1)
    
    response = test_client.get("/search", data=dict(
        title=existing_doctor.name
    ), follow_redirects=True)

    assert 200 == response.status_code

def test_search_not_found(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
    
    response = test_client.get("/search", data=dict(title="doctor_not_exsit"))

    assert b'cannot be found' in response.data

def test_search_empty_text(test_client):
    patient = Patient.query.get(101)
    email = patient.email
    password = 'password'
    # login first
    test_client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
    
    response = test_client.get("/search", data=None)

    assert 200 == response.status_code
