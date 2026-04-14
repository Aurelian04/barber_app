from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import BarberWeeklySchedule, LunchBreak, BarberScheduleException

class AvailabilityApiTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        
        self.barber_user = self.User.objects.create_user(
            username="barber",
            email="barber@example.com",
            password="testpass123",
            is_barber=True,
        )
        
    def test_barber_can_create_weekly_schedule(self):
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekday": 1,
            "start_time": "9:00:00",
            "end_time": "17:00",
            "is_active": True,
        }
        
        url = "/api/barber/weekly-schedules/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BarberWeeklySchedule.objects.count(), 1)
        
    def test_barber_can_get_schedule(self):
        day_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        self.client.force_authenticate(user=self.barber_user)
        
        url = "/api/barber/weekly-schedules/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], day_schedule.id)
        
    def test_barber_can_partial_update_schedule(self):    
        day_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekday": 1,
            "start_time": "8:00:00",
            "end_time": "16:00:00",
            "is_active": True,
        }
        
        url = f"/api/barber/weekly-schedules/{day_schedule.id}/"
        
        response = self.client.patch(url, payload, format="json")
        
        day_schedule.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_time"], "08:00:00")
        self.assertEqual(str(day_schedule.start_time), "08:00:00")
        
    def test_barber_can_fully_update_schedule(self):
        day_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekday": 1,
            "start_time": "8:00:00",
            "end_time": "16:00:00",
            "is_active": False,
        }
        
        url = f"/api/barber/weekly-schedules/{day_schedule.id}/"
        
        response = self.client.put(url, payload, format="json")
        
        day_schedule.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_time"], "08:00:00")
        self.assertEqual(str(day_schedule.start_time), "08:00:00")
        self.assertEqual(str(day_schedule.end_time), "16:00:00")
        self.assertEqual(str(day_schedule.is_active), "False")
        
    def test_barber_can_delete_schedule(self):
        day_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        url = f"/api/barber/weekly-schedules/{day_schedule.id}/"
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BarberWeeklySchedule.objects.filter(id=day_schedule.id).exists(), False)