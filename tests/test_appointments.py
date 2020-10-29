import tests.factories as factories
from virtual_hospital.models import *
from datetime import date

def test_appointments():
    # wip

    client = app.test_client()
    client.post('/login', data=dict(
            email="alatest1@test.com",
            password="Qwerty1!
        ), follow_redirects=True)
    # patient client

    client2 = app.test_client()
    client2.post('/login', data=dict(
            email="alatest2@test.com",
            password="Qwerty1!
        ), follow_redirects=True)
    # doctor client

    user = User.query.filter_by(email="alatest2@test.com").first()
    searchString = '/profile?id=' + user.id
    
    response1 = client.get(searchString)
    assert response1.status_code == 200 # checks if getting the profile loads properly

    appointmentURIString = 'newappointment?doctor_id=' + user.id        

    response1 = client.get(appointmentURIString)
    assert response1.status_code == 200 # checks if making a new appointment loads properly
    data = response.get_data(as_text = True)
    
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    assert d1 in data # checks for if today's date is properly in webpage
    
    client.post('/newappointment', data=dict(), follow_redirects=True)
    # new appointment stuff

    
    
    
