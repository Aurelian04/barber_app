from .models import BarberWeeklySchedule, BarberScheduleException

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
            (weekly_schedule.start_time, weekly_schedule.end_time),
            (lunch.end_time, weekly_schedule.end_time),
        ]
        
    return intervals