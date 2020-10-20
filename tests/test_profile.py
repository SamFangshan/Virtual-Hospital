import tests.factories as factories
from virtual_hospital.models import *

def login(test_client, user_type):
    if user_type == "patient":
        patient = Patient.query.get(10001)
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

def test_update_profile_patient_success(test_client):
    login(test_client, 'patient')

    payload = {
        'name': 'new_name',
        'phone_number': '12345678',
        'nric': 'S1234567B',
        'gender': 'Male',
        'date_of_birth': '01/01/1900'
    }

    response = test_client.post("/setprofile", data=payload, follow_redirects=True)
    assert b'Profile updated' in response.data

def test_update_profile_patient_missing_field(test_client):
    login(test_client, 'patient')

    payload = {
        'name': 'new_name',
        'phone_number': '12345678',
        'nric': 'S1234567B',
        'gender': 'Male',
    }

    response = test_client.post("/setprofile", data=payload, follow_redirects=True)
    assert response.status_code == 400

def test_update_profile_patient_invalid_input(test_client):
    login(test_client, 'patient')

    payload_name = {
        'name': 'new_name_greater_than_20_character',
        'phone_number': '12345678',
        'nric': 'S1234567B',
        'gender': 'Male',
        'date_of_birth': '01/01/1900'
    }

    payload_nric = {
        'name': 'new_name',
        'phone_number': '12345678',
        'nric': 'S1234567B10',
        'gender': 'Male',
        'date_of_birth': '01/01/1900'
    }

    payload_gender = {
        'name': 'new_name',
        'phone_number': '12345678',
        'nric': 'S1234567B',
        'gender': 'Maleeee',
        'date_of_birth': '01/01/1900'
    }

    payload = {
        'name': 'new_name',
        'phone_number': '123456789000000000',
        'nric': 'S1234567B',
        'gender': 'Male',
        'date_of_birth': '01/01/1900'
    }

    response = test_client.post("/setprofile", data=payload_name, follow_redirects=True)
    assert b'Invalid input' in response.data

    response = test_client.post("/setprofile", data=payload_nric, follow_redirects=True)
    assert b'Invalid input' in response.data

    response = test_client.post("/setprofile", data=payload_gender, follow_redirects=True)
    assert b'Invalid input' in response.data

    response = test_client.post("/setprofile", data=payload_name, follow_redirects=True)
    assert b'Invalid input' in response.data

def test_update_profile_doctor_success(test_client):
    login(test_client, 'doctor')

    payload = {
        'name': 'new_name',
        'phone_number': '12345678',
        'nric': 'S1234567B',
        'gender': 'Male',
        'credentials': 'credentials',
        'specialties': 'Ear, Nose & Throat',
        'office_hour_start_time': '08:30',
        'office_hour_end_time': '18:00',
        'department_id': 1
    }

    response = test_client.post("/setprofile", data=payload, follow_redirects=True)
    assert b'Profile updated' in response.data

def test_update_profile_doctor_missing_field(test_client):
    login(test_client, 'doctor')

    payload = {
        'name': 'new_name',
        'phone_number': '12345678',
        'nric': 'S1234567B',
        'gender': 'Male',
        'credentials': 'credentials',
        'specialties': 'Ear, Nose & Throat',
        'office_hour_start_time': '08:30',
        'office_hour_end_time': '18:00'
    }

    response = test_client.post("/setprofile", data=payload, follow_redirects=True)
    assert response.status_code == 400