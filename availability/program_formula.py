from .models import BarberWeeklySchedule, BarberScheduleException

from appointments.models import Appointment
from services.models import Service

from datetime import datetime, timedelta

from django.utils import timezone

def get_barber_working_intervals_for_date(barber, date):
    """
    Returns working intervals for a barber in a day.
    
    Output:
    [
        (start_time, end_time),
        (start_time, end_time),
    ]
    
    If barber dosent work:
    []
    """
    
    exceptions = BarberScheduleException.objects.filter(
        barber=barber,
        date=date,
    ).order_by("start_time")
    
    if exceptions.exists():
        if exceptions.filter(is_day_off=True).exists():
            return[]
        
        return [
            (exception.start_time, exception.end_time)
            for exception in exceptions
            if not exception.is_day_off
        ]
        
    weekday = date.isoweekday()
    
    weekly_schedule = BarberWeeklySchedule.objects.filter(
        barber=barber,
        weekday=weekday,
        is_active=True,
    ).first()
    
    if weekly_schedule is None:
        return []
    
    intervals = [
        (weekly_schedule.start_time, weekly_schedule.end_time)
    ]
    
    if hasattr(weekly_schedule, "lunch_break"):
        lunch = weekly_schedule.lunch_break
        
        intervals = [
            (weekly_schedule.start_time, lunch.start_time),
            (lunch.end_time, weekly_schedule.end_time),
        ]
        
    return intervals


def get_available_slots_for_date(barber, date, service):
    working_intervals = get_barber_working_intervals_for_date(barber, date)
    
    service_duration = service.duration_minutes
    
    booked_appointments = Appointment.objects.filter(
        status=Appointment.Status.BOOKED,
        barber=barber,
        start_time__date=date,
    )
    
    occupied_intervals = []
    for appointment in booked_appointments:
        occupied_intervals.append(
            (appointment.start_time, appointment.end_time)
            )
        
    available_slots = []
    
    for interval_start, interval_end in working_intervals:
        current_slot_start = interval_start
    
        current_slot_start_datetime = timezone.make_aware(
            datetime.combine(date, current_slot_start)
        )
        
        current_slot_end_datetime = current_slot_start_datetime + timedelta(
            minutes=service_duration
        )
        
        interval_end_datetime = timezone.make_aware(
            datetime.combine(date, interval_end)
        )
        
        
        while current_slot_end_datetime <= interval_end_datetime:
            slot_is_available = True
            
            for occupied_start, occupied_end in occupied_intervals:
                if (
                    current_slot_start_datetime < occupied_end
                    and current_slot_end_datetime > occupied_start
                ):
                    slot_is_available = False
                    break
                
            if slot_is_available:
                available_slots.append(current_slot_start_datetime)
                
            current_slot_start_datetime = current_slot_start_datetime + timedelta(minutes=15)
            current_slot_end_datetime = current_slot_start_datetime + timedelta(minutes=service_duration)
            
    return available_slots