from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import BarberWeeklySchedule, LunchBreak, BarberScheduleException

class AvailabilityApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model()
        
        self.barber_user = self.User.objects.create_user(
            username="barber",
            email="barber@example.com",
            password="testpass123",
            is_barber=True,
        )
        
    def test_barber_can_create_weekly_schedule(self):
        self.client.force_authenticate(barber=self.barber_user)
        
        payload = {
            "weekday": "Monday",
            "start_time": "9:00",
            "end_time": "17:00",
            "is_active": "True",
        }
        
        url = (r"/api/barber/weekly-schedules/")
        
        response = self.client.post(url, payload, format="json")
        
        