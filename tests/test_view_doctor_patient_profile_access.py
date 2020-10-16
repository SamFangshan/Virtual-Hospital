import tests.factories as factories
from virtual_hospital.models import *

def login(test_client, user_type):
    if user_type == "patient":
        patient = Patient.query.get(101)
        email = patient.email
        password = 'password'
    elif user_type == "doctor":
        doctor = Doctor.query.get(1)
        email = doctor.email
        password = 'password'

    test_client.post('/login', data=dict(
                email=email,
                password=password
            ), follow_redirects=True)

def test_view_profile_without_login(test_client):
    test_client.get("/logout", follow_redirects=True)

    response = test_client.get("/profile?id=10001", follow_redirects=True)
    assert b'Please log in to access this page' in response.data

def test_view_own_profile_as_patient(test_client):
    login(test_client, "patient")

    response = test_client.get("/profile?id=101", follow_redirects=True)
    assert response.status_code == 200

def test_view_other_patient_profile_as_patient(test_client):
    login(test_client, "patient")

    response = test_client.get("/profile?id=10001", follow_redirects=True)
    assert response.status_code == 403

def test_view_patient_profile_as_doctor(test_client):
    login(test_client, "doctor")

    response = test_client.get("/profile?id=10001", follow_redirects=True)
    assert response.status_code == 200

def test_view_doctor_profile_as_doctor(test_client):
    login(test_client, "doctor")

    response = test_client.get("/profile?id=2", follow_redirects=True)
    assert response.status_code == 200

