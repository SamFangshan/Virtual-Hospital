from datetime import datetime

import pytest
from virtual_hospital.cronjobs import generate_time_slots
from virtual_hospital.models import *


@pytest.mark.run(order=4)
def test_generate_time_slots(_db):
    today = datetime.today().date()
    generate_time_slots()
    days_generated_for_doctor_1 = 9 - today.weekday() if today.weekday() <= 4 else 5
    assert AppointmentTimeSlot.query.filter_by(doctor_id=1).count() == 19 * days_generated_for_doctor_1 + 1
    assert AppointmentTimeSlot.query.filter_by(doctor_id=2).count() == 0
    assert AppointmentTimeSlot.query.filter_by(doctor_id=3).count() == 20 * (10 - today.weekday())
