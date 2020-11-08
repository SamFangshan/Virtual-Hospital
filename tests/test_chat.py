import tests.factories as factories
from virtual_hospital.models import *
from datetime import date
from virtual_hospital import app

def test_chat(test_client):

    client = test_client
    client.post('/login', data=dict(
            email="alatest1@test.com",
            password="Qwerty1!"
        ), follow_redirects=True)
    # patient client

    client2 = app.test_client()
    client2.post('/login', data=dict(
            email="alatest2@test.com",
            password="Qwerty1!"
        ), follow_redirects=True)
    # doctor client

    user = User.query.filter_by(email="alatest2@test.com").first()
    user2 = User.query.filter_by(email="alatest1@test.com").first()
    searchString = '/profile?id=' + str(user.id)

    response1 = client.get(searchString)
    assert response1.status_code == 200 # checks if getting the profile loads properly

    appointmentURIString = 'newappointment?doctor_id=' + str(user.id)

    response1 = client.get(appointmentURIString)
    assert response1.status_code == 200 # checks if making a new appointment loads properly
    data = response1.get_data(as_text = True)

    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    assert d1 in data # checks for if today's date is properly in webpage
    time_slot_data = AppointmentTimeSlot.query.filter_by(doctor_id=user.id).first()

    response2 = client.post('/newappointment?doctor_id={}'.format(user.id), data=dict(
            doctor_id=user.id,
            appointment_time_slot_id=time_slot_data.id
        ), follow_redirects=True)
    # new appointment stuff

    assert response2.status_code == 200
    assert 'Appointment booked.' in response2.get_data(as_text = True) # checks if appointment has been booked by client

    response3 = client2.get('appointments')
    assert response3.status_code == 200

    data = response3.get_data(as_text = True)
    fullString = user2.name + ' (Queue: '
    assert fullString in data
