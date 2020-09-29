import datetime

from virtual_hospital import db
from virtual_hospital.models import AppointmentTimeSlot


def generate_time_slots_for_a_day(date, start_time, end_time):
    """This function generates appointments time slots in 30-minute intervals given a specific date,
       start time, and end time. Assuming start_time and end_time are in multiples of 30 minutes, and
       start_time is earlier than end_time.

    Parameters
    ----------
    date : datetime.datetime
        The date to generate time slots for.
    start_time : str
        Office hour start time. (e.g. 08:00)
    end_time : str
        Office hour end time.  (e.g. 17:00)

    Returns
    -------
    list
        A list of tuples of start time and end time of time slots.

    """
    start_hour_text, start_minute_text = start_time.split(':')
    start_hour, start_minute = int(start_hour_text), int(start_minute_text)

    end_hour_text, end_minute_text = end_time.split(':')
    end_hour, end_minute = int(end_hour_text), int(end_minute_text)

    time_slots = list()
    cur_time = datetime.datetime(date.year, date.month, date.day, start_hour, start_minute)
    while cur_time < datetime.datetime(date.year, date.month, date.day, end_hour, end_minute):
        next_time = cur_time + datetime.timedelta(minutes=30)  # time slots in 30 min intervals
        time_slots.append((cur_time, next_time))
        cur_time = next_time
    return time_slots


def time_slots_exist(doctor_id, date):
    """Checks whether any time slots are already created for a doctor on a specific date.

    Parameters
    ----------
    doctor_id : int
        The id of the doctor.
    date : type
        Date on which time slots are created.

    Returns
    -------
    bool
        Whether or not a time slot exists on a specified date for a specific doctor.

    """
    time_slot = AppointmentTimeSlot.query.filter(
        db.func.date(AppointmentTimeSlot.appointment_start_time) == date,
        AppointmentTimeSlot.doctor_id == doctor_id
    ).first()

    if time_slot is None:
        return False
    else:
        return True


def get_dates_of_current_and_next_weeks(date):
    """This function determines the dates of weekdays of current week and next week, from the given
       current day onwards.

    Parameters
    ----------
    date : datetime.datetime
        Current date.

    Returns
    -------
    list
        A list datetime objects.

    """
    dates = list()
    # current week
    while date.weekday() <= 4:  # is weekday
        dates.append(date)
        date += datetime.timedelta(days=1)
    # skip weekends of current week
    while date.weekday() != 0:
        date += datetime.timedelta(days=1)
    # next week
    while date.weekday() <= 4:  # is weekday
        dates.append(date)
        date += datetime.timedelta(days=1)
    return dates
