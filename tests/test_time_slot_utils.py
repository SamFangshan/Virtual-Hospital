import datetime

from virtual_hospital.models import *
from virtual_hospital.utils.time_slot_utils import *


def test_time_slots_exist(_db):
    date = datetime.datetime.today().date()
    assert time_slots_exist(1, date)
    assert not time_slots_exist(1, date + datetime.timedelta(days=1))
    assert time_slots_exist(2, date)
    assert not time_slots_exist(2, date + datetime.timedelta(days=1))
    assert not time_slots_exist(3, date)
    assert not time_slots_exist(4, date)
    assert not time_slots_exist(5, date)
