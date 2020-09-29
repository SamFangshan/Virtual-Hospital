import datetime
import pytest

from virtual_hospital.models import *
from virtual_hospital.utils.time_slot_utils import *

@pytest.mark.run(order=3)
def test_time_slots_exist(_db):
    date = datetime.datetime.today().date()
    # doctor with time slots already generated on a date
    assert time_slots_exist(1, date)
    # same doctor, but no other time slots in another day
    assert not time_slots_exist(1, date + datetime.timedelta(days=1))
    # doctor with completely no time slots
    assert not time_slots_exist(2, date)


def test_generate_time_slots_for_a_day():
    # assuming the starting minute and ending minute are multiples of 30 minutes
    date = datetime.datetime.today().date()
    time_slots = generate_time_slots_for_a_day(date, '12:30', '14:00')  # multiple consecutive slots
    correct_time_slots = [(datetime.datetime(date.year, date.month, date.day, 12, 30),
                           datetime.datetime(date.year, date.month, date.day, 13, 00)),
                          (datetime.datetime(date.year, date.month, date.day, 13, 00),
                           datetime.datetime(date.year, date.month, date.day, 13, 30)),
                          (datetime.datetime(date.year, date.month, date.day, 13, 30),
                           datetime.datetime(date.year, date.month, date.day, 14, 00))]
    assert time_slots == correct_time_slots

    time_slots = generate_time_slots_for_a_day(date, '13:30', '14:00')  # one slot
    correct_time_slots = [(datetime.datetime(date.year, date.month, date.day, 13, 30),
                           datetime.datetime(date.year, date.month, date.day, 14, 00))]
    assert time_slots == correct_time_slots


def test_get_dates_of_current_and_next_weeks():
    date = datetime.datetime(2020, 1, 6)  # Monday
    dates = get_dates_of_current_and_next_weeks(date)
    correct_dates = [datetime.datetime(2020, 1, 6),  # weekdays of current week
                     datetime.datetime(2020, 1, 7),
                     datetime.datetime(2020, 1, 8),
                     datetime.datetime(2020, 1, 9),
                     datetime.datetime(2020, 1, 10),  # weekdays of next week
                     datetime.datetime(2020, 1, 13),
                     datetime.datetime(2020, 1, 14),
                     datetime.datetime(2020, 1, 15),
                     datetime.datetime(2020, 1, 16),
                     datetime.datetime(2020, 1, 17)]
    assert dates == correct_dates

    date = datetime.datetime(2020, 1, 7)  # Tuesday
    dates = get_dates_of_current_and_next_weeks(date)
    correct_dates.pop(0)  # This Monday eliminated
    assert dates == correct_dates

    date = datetime.datetime(2020, 1, 8)  # Wednesday
    dates = get_dates_of_current_and_next_weeks(date)
    correct_dates.pop(0)  # This Tuesday eliminated
    assert dates == correct_dates

    date = datetime.datetime(2020, 1, 9)  # Thursday
    dates = get_dates_of_current_and_next_weeks(date)
    correct_dates.pop(0)  # This Wednesday eliminated
    assert dates == correct_dates

    date = datetime.datetime(2020, 1, 10)  # Friday
    dates = get_dates_of_current_and_next_weeks(date)
    correct_dates.pop(0)  # This Thursday eliminated
    assert dates == correct_dates

    date = datetime.datetime(2020, 1, 11)  # Saturday
    dates = get_dates_of_current_and_next_weeks(date)
    correct_dates.pop(0)  # This Friday eliminated
    assert dates == correct_dates

    date = datetime.datetime(2020, 1, 11)  # Sunday
    dates = get_dates_of_current_and_next_weeks(date)
    assert dates == correct_dates
