from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import BarberWeeklySchedule, LunchBreak, BarberScheduleException

class BarberWeeklyScheduleApiTests(APITestCase):
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
        
    def test_barber_cannot_access_other_barber_schedule(self):
        barber1= self.User.objects.create_user(
            username="barber1",
            email="barber1@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        barber2 = self.User.objects.create_user(
            username="barber2",
            email="barber2@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        schedule = BarberWeeklySchedule.objects.create(
            barber=barber1,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        self.client.force_authenticate(user=barber2)
        
        url = f"/api/barber/weekly-schedules/{schedule.id}/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_barber_cannot_see_another_barber_schedule_in_list(self):
        barber1= self.User.objects.create_user(
            username="barber1",
            email="barber1@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        barber2 = self.User.objects.create_user(
            username="barber2",
            email="barber2@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        schedule = BarberWeeklySchedule.objects.create(
            barber=barber1,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        schedule2 = BarberWeeklySchedule.objects.create(
            barber=barber2,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        self.client.force_authenticate(user=barber1)
        
        url = "/api/barber/weekly-schedules/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], schedule.id)
        self.assertEqual(response.data[0]["barber"], barber1.id)
        
    def test_barber_cannot_update_annother_barber_schedule(self):
        barber1= self.User.objects.create_user(
            username="barber1",
            email="barber1@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        barber2 = self.User.objects.create_user(
            username="barber2",
            email="barber2@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        schedule = BarberWeeklySchedule.objects.create(
            barber=barber1,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        self.client.force_authenticate(user=barber2)
        
        payload = {
            "weekday": 1,
            "start_time": "8:00:00",
            "end_time": "16:00:00",
            "is_active": True,
        }
        
        url = f"/api/barber/weekly-schedules/{schedule.id}/"
        
        response = self.client.patch(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        schedule.refresh_from_db()
        
        self.assertEqual(str(schedule.start_time), "09:00:00")
        self.assertEqual(str(schedule.end_time), "17:00:00")
        
    def test_barber_cannot_delete_annother_barber_schedule(self):
        barber1= self.User.objects.create_user(
            username="barber1",
            email="barber1@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        barber2 = self.User.objects.create_user(
            username="barber2",
            email="barber2@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        schedule = BarberWeeklySchedule.objects.create(
            barber=barber1,
            weekday=1,
            start_time="9:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        self.client.force_authenticate(user=barber2)
        
        url = f"/api/barber/weekly-schedules/{schedule.id}/"
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        schedule.refresh_from_db()
        
        self.assertEqual(BarberWeeklySchedule.objects.filter(id=schedule.id).exists(), True)
        
    def test_cannot_create_schedule_with_invalid_time(self):
        self.client.force_authenticate(user=self.barber_user)

        payload = {
            "weekday": 1,
            "start_time": "09:00:00",
            "end_time": "08:00:00",
            "is_active": True,
        }

        url = "/api/barber/weekly-schedules/"

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("__all__", response.data)
        

class LunchBreakApiTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        
        self.barber_user = self.User.objects.create_user(
            username="barber",
            email="barber@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        self.weekly_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=1,
            start_time="09:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        self.barber_user2 = self.User.objects.create(
            username="barber2",
            email="test2@barber.com",
            password="testpass112",
            is_barber=True,
        )
        
    def test_barber_can_create_lunch_break(self):
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekly_schedule": self.weekly_schedule.id,
            "start_time": "12:00:00",
            "end_time": "12:30:00",
        }
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LunchBreak.objects.count(), 1)
        self.assertEqual(response.data["weekly_schedule"], self.weekly_schedule.id)
        
    def test_barber_can_get_lunch_break(self):
        lunch = LunchBreak.objects.create(
            weekly_schedule = self.weekly_schedule,
            start_time = "12:00:00",
            end_time = "12:30:00"
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], lunch.id)
        ids = [item["id"] for item in response.data]
        self.assertIn(lunch.id, ids)
        
    def test_barber_can_partial_edit_lunch_break(self):
        lunch = LunchBreak.objects.create(
            weekly_schedule = self.weekly_schedule,
            start_time = "12:00:00",
            end_time = "12:30:00"
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekly_schedule": self.weekly_schedule.id,
            "start_time": "12:10:00",
            "end_time": "12:30:00",
        }
        
        url = f"/api/barber/lunch-breaks/{lunch.id}/"
        
        response = self.client.patch(url, payload, format="json")
        
        lunch.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_time"], "12:10:00")
        self.assertEqual(str(lunch.start_time), "12:10:00")
        self.assertEqual(str(lunch.end_time), "12:30:00")
        
    def test_barber_can_fully_edit_lunch_break(self):
        lunch = LunchBreak.objects.create(
            weekly_schedule = self.weekly_schedule,
            start_time = "12:00:00",
            end_time = "12:30:00"
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekly_schedule": self.weekly_schedule.id,
            "start_time": "12:30:00",
            "end_time": "13:00:00",
        }
        
        url = f"/api/barber/lunch-breaks/{lunch.id}/"
        
        response = self.client.put(url, payload, format="json")
        
        lunch.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_time"], "12:30:00")
        self.assertEqual(str(lunch.start_time), "12:30:00")
        self.assertEqual(str(lunch.end_time), "13:00:00")
        
    def test_barber_can_delete_lunch_break(self):
        lunch = LunchBreak.objects.create(
            weekly_schedule = self.weekly_schedule,
            start_time = "12:00:00",
            end_time = "12:30:00"
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        url = f"/api/barber/lunch-breaks/{lunch.id}/"
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LunchBreak.objects.filter(id=lunch.id).exists(), False)
        
    def test_barber_cannot_see_another_barber_lunch_break(self):
        barber2 = self.barber_user2
        
        lunchBreak = LunchBreak.objects.create(
            weekly_schedule=self.weekly_schedule,
            start_time="12:00:00",
            end_time="12:30:00",
        )
        
        self.client.force_authenticate(user=barber2)
        
        url = f"/api/barber/lunch-breaks/{lunchBreak.id}/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        
    def test_barber_cannot_create_lunch_break_over_another_barber_schedule(self):
        weekly_schedule_1 = self.weekly_schedule

        self.client.force_authenticate(user=self.barber_user2)

        payload = {
            "weekly_schedule": weekly_schedule_1.id,
            "start_time": "12:00:00",
            "end_time": "12:30:00",
        }

        url = "/api/barber/lunch-breaks/"

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("weekly_schedule", response.data)
        self.assertEqual(LunchBreak.objects.count(), 0)
        
    def test_barber_cannot_modify_another_barber_lunch_break(self):
        lunchBreak1 = LunchBreak.objects.create(
            weekly_schedule=self.weekly_schedule,
            start_time="12:00:00",
            end_time="12:30:00",
        )
        
        self.client.force_authenticate(user=self.barber_user2)
        
        payload = {
            "weekly_schedule": self.weekly_schedule.id,
            "start_time": "12:30:00",
            "end_time": "13:00:00",
        }
        
        url = f"/api/barber/lunch-breaks/{lunchBreak1.id}/"
        
        response = self.client.patch(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(str(lunchBreak1.start_time), "12:00:00")
        
    def test_barber_cannot_delete_another_barber_lunch_break(self):
        lunchBreak1 = LunchBreak.objects.create(
            weekly_schedule=self.weekly_schedule,
            start_time="12:00:00",
            end_time="12:30:00",
        )
        
        self.client.force_authenticate(user=self.barber_user2)
        
        url = f"/api/barber/lunch-breaks/{lunchBreak1.id}/"
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(LunchBreak.objects.filter(id=lunchBreak1.id).exists())
        
    def test_non_barber_cannot_create_lunch_break(self):
        user1 = self.User.objects.create_user(
            username="User",
            email="user@gmail.com",
            password="pass12U",
            is_barber=False,
        )
        
        self.client.force_authenticate(user=user1)
        
        payload = {
            "weekly_schedule": self.weekly_schedule.id,
            "start_time": "12:00:00",
            "end_time": "12:30:00",
        }
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(LunchBreak.objects.count(), 0)
        
    def test_staff_can_see_all_lunch_breaks(self):
        weeklySchedule2 = BarberWeeklySchedule.objects.create(
            barber=self.barber_user2,
            weekday=1,
            start_time="09:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        lunchBreak1 = LunchBreak.objects.create(
            weekly_schedule=self.weekly_schedule,
            start_time="12:00:00",
            end_time="12:30:00",
        )
        
        lunchBreak2 = LunchBreak.objects.create(
            weekly_schedule=weeklySchedule2,
            start_time="12:00:00",
            end_time="12:30:00",
        )
        
        staffUser = self.User.objects.create_superuser(
            username="User",
            email="user@gmail.com",
            password="pass12U",
            is_barber=False,
        )
        
        self.client.force_authenticate(user=staffUser)
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        ids = [item["id"] for item in response.data]
        
        self.assertEqual(len(ids), 2)
        self.assertIn(lunchBreak1.id, ids)
        self.assertIn(lunchBreak2.id, ids)
    
    def test_start_time_less_than_end_time(self):
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekly_schedule": self.weekly_schedule.id,
            "start_time": "12:30:00",
            "end_time": "12:00:00",
        }
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("__all__", response.data)
        
    def test_barber_cannot_create_lunch_break_before_and_after_program(self):
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekly_schedule": self.weekly_schedule.id,
            "start_time": "7:00:00",
            "end_time": "19:15:00",
        }
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_barber_cannot_create_lunch_break_to_inactive_schedule(self):
        schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=2,
            start_time="08:00:00",
            end_time="18:00:00",
            is_active=False,
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "weekly_schedule": schedule.id,
            "start_time": "12:00:00",
            "end_time": "12:30:00",
        }
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("weekly_schedule", response.data)
        
    def test_barber_cannot_create_lunch_break_with_empty_weekly_schedule(self):
        self.client.force_authenticate(user=self.barber_user2)
        
        payload = {
            "weekly_schedule": "",
            "start_time": "12:00:00",
            "end_time": "12:30:00",
        }
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("weekly_schedule", response.data)
        
    def test_barber_cannot_create_lunch_break_without_weekly_schedule(self):
        self.client.force_authenticate(user=self.barber_user2)
        
        payload = {
            "start_time": "12:00:00",
            "end_time": "12:30:00",
        }
        
        url = "/api/barber/lunch-breaks/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("weekly_schedule", response.data)
        
    
class BarberScheduleExceptionApiTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        
        self.barber_user = self.User.objects.create_user(
            username="barber",
            email="barber@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        self.barber_user2 = self.User.objects.create_user(
            username="barber2",
            email="barber2@example.com",
            password="testpass1234",
            is_barber=True,
        )
        
    def test_barber_can_create_schedule_exception_returns_201(self):
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "date": "2026-01-01",
            "start_time": "10:00:00",
            "end_time": "15:00:00",
            "is_day_off": False,
            "reason": "Test"
        }
        
        url = "/api/barber/exception-schedules/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["date"], "2026-01-01")
        self.assertEqual(BarberScheduleException.objects.count(), 1)
        
    def test_barber_can_get_schedule_exception_returns_200(self):
        exception1 = BarberScheduleException.objects.create(
            barber=self.barber_user,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="15:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        url = "/api/barber/exception-schedules/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], exception1.id)
        ids = [item["id"] for item in response.data]
        self.assertIn(exception1.id, ids)
        
    def test_barber_can_partial_update_schedule_exception_returns_200(self):
        exception1 = BarberScheduleException.objects.create(
            barber=self.barber_user,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="12:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "date": "2026-01-01",
            "start_time": "10:00:00",
            "end_time":"15:00:00",
            "is_day_off": False,
            "reason": "Test",
        }
        
        url = f"/api/barber/exception-schedules/{exception1.id}/"
        
        response = self.client.patch(url, payload, format="json")
        
        exception1.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["end_time"], "15:00:00")
        self.assertEqual(str(exception1.end_time), "15:00:00")
        
    def test_barber_can_fully_update_schedule_exception_returns_200(self):
        exception1 = BarberScheduleException.objects.create(
            barber=self.barber_user,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="12:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "date": "2026-01-09",
            "start_time": None,
            "end_time": None,
            "is_day_off": True,
            "reason": "More",
        }
        
        url = f"/api/barber/exception-schedules/{exception1.id}/"
        
        response = self.client.put(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_day_off"])
        self.assertIsNone(response.data["start_time"])
        self.assertIsNone(response.data["end_time"])
        
        exception1.refresh_from_db()
        self.assertTrue(exception1.is_day_off)
        self.assertIsNone(exception1.start_time)
        self.assertIsNone(exception1.end_time)
        
    def test_barber_can_delete_schedule_exception_returns_204(self):
        exception1 = BarberScheduleException.objects.create(
            barber=self.barber_user,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="12:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        url = f"/api/barber/exception-schedules/{exception1.id}/"
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BarberScheduleException.objects.filter(id=exception1.id).exists())
        
    def test_barber_cannot_update_another_barbers_schedule_exception_returns_404(self):
        sch_exception1 = BarberScheduleException.objects.create(
            barber=self.barber_user2,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="12:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        payload = {
            "date": "2026-01-01",
            "start_time": "11:00:00",
            "end_time": "15:00:00",
            "is_day_off": False,
            "reason": "Test",
        }
        
        url = f"/api/barber/exception-schedules/{sch_exception1.id}/"
        
        response = self.client.patch(url, payload, format="json")
        
        sch_exception1.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(str(sch_exception1.start_time), "10:00:00")
        
    def test_barber_cannot_delete_another_barbers_schedule_exception_retruns_404(self):
        sch_exception1 = BarberScheduleException.objects.create(
            barber=self.barber_user2,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="12:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        url = f"/api/barber/exception-schedules/{sch_exception1.id}/"
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(str(sch_exception1.start_time), "10:00:00")
        self.assertTrue(BarberScheduleException.objects.filter(id=sch_exception1.id).exists())
        
    def test_barber_cannot_get_another_barber_schedule_exception_returns_404(self):
        self.client.force_authenticate(user=self.barber_user)
        
        sch_exception1 = BarberScheduleException.objects.create(
            barber=self.barber_user2,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="12:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        url = f"/api/barber/exception-schedules/{sch_exception1.id}/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_non_barber_cannot_create_schedule_exception_returns_403(self):
        user1 = self.User.objects.create_user(
            username="Marian",
            email="marian@gmail.com",
            password="pass9865",
            is_barber=False,
        )
        
        self.client.force_authenticate(user=user1)
        
        payload = {
            "date": "2026-01-01",
            "start_time": "11:00:00",
            "end_time": "15:00:00",
            "is_day_off": False,
            "reason": "Test",
        }
        
        url = "/api/barber/exception-schedules/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_staff_can_see_all_schedule_exceptions_returns_200(self):
        user1 = self.User.objects.create_superuser(
            username="Marian",
            email="marian@gmail.com",
            password="pass9865",
            is_barber=True,
        )
        
        sch_exception1 = BarberScheduleException.objects.create(
            barber=self.barber_user,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="12:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        sch_exception2 = BarberScheduleException.objects.create(
            barber=self.barber_user2,
            date="2026-01-01",
            start_time="10:00:00",
            end_time="12:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        self.client.force_authenticate(user=user1)
        
        url = "/api/barber/exception-schedules/"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        ids = [item["id"] for item in response.data]
        self.assertIn(sch_exception1.id, ids)
        self.assertIn(sch_exception2.id, ids)
        
    def test_barber_cannot_create_day_off_exception_with_start_and_end_time_returns_400(self):
        self.client.force_authenticate(user=self.barber_user)

        payload = {
            "date": "2026-01-01",
            "start_time": "10:00:00",
            "end_time": "12:00:00",
            "is_day_off": True,
            "reason": "Day off",
        }

        response = self.client.post(
            "/api/barber/exception-schedules/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_barber_can_create_day_off_exception_without_start_and_end_time_returns_201(self):
        self.client.force_authenticate(user=self.barber_user)

        payload = {
            "date": "2026-01-01",
            "start_time": None,
            "end_time": None,
            "is_day_off": True,
            "reason": "Day off",
        }

        response = self.client.post(
            "/api/barber/exception-schedules/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_day_off"])
        self.assertIsNone(response.data["start_time"])
        self.assertIsNone(response.data["end_time"])


    def test_barber_cannot_create_working_exception_without_start_time_returns_400(self):
        self.client.force_authenticate(user=self.barber_user)

        payload = {
            "date": "2026-01-01",
            "start_time": None,
            "end_time": "15:00:00",
            "is_day_off": False,
            "reason": "Custom hours",
        }

        response = self.client.post(
            "/api/barber/exception-schedules/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_barber_cannot_create_working_exception_without_end_time_returns_400(self):
        self.client.force_authenticate(user=self.barber_user)

        payload = {
            "date": "2026-01-01",
            "start_time": "10:00:00",
            "end_time": None,
            "is_day_off": False,
            "reason": "Custom hours",
        }

        response = self.client.post(
            "/api/barber/exception-schedules/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_barber_cannot_create_schedule_exception_with_start_time_after_end_time_returns_400(self):
        self.client.force_authenticate(user=self.barber_user)

        payload = {
            "date": "2026-01-01",
            "start_time": "16:00:00",
            "end_time": "12:00:00",
            "is_day_off": False,
            "reason": "Invalid hours",
        }

        response = self.client.post(
            "/api/barber/exception-schedules/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_barber_cannot_create_schedule_exception_with_same_start_and_end_time_returns_400(self):
        self.client.force_authenticate(user=self.barber_user)

        payload = {
            "date": "2026-01-01",
            "start_time": "12:00:00",
            "end_time": "12:00:00",
            "is_day_off": False,
            "reason": "Invalid hours",
        }

        response = self.client.post(
            "/api/barber/exception-schedules/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_barber_can_create_multiple_working_exceptions_for_same_date_returns_201(self):
        self.client.force_authenticate(user=self.barber_user)

        payload1 = {
            "date": "2026-01-01",
            "start_time": "09:00:00",
            "end_time": "11:00:00",
            "is_day_off": False,
            "reason": "Morning interval",
        }

        payload2 = {
            "date": "2026-01-01",
            "start_time": "14:00:00",
            "end_time": "16:00:00",
            "is_day_off": False,
            "reason": "Afternoon interval",
        }

        response1 = self.client.post("/api/barber/exception-schedules/", payload1, format="json")
        response2 = self.client.post("/api/barber/exception-schedules/", payload2, format="json")

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            BarberScheduleException.objects.filter(
                barber=self.barber_user,
                date="2026-01-01",
            ).count(),
            2,
        )
        
    def test_barber_cannot_create_overlapping_working_exceptions_for_same_date_returns_400(self):
        BarberScheduleException.objects.create(
            barber=self.barber_user,
            date="2026-01-01",
            start_time="09:00:00",
            end_time="11:00:00",
            is_day_off=False,
            reason="Morning interval",
        )

        self.client.force_authenticate(user=self.barber_user)

        payload = {
            "date": "2026-01-01",
            "start_time": "10:30:00",
            "end_time": "12:00:00",
            "is_day_off": False,
            "reason": "Overlapping interval",
        }

        response = self.client.post(
            "/api/barber/exception-schedules/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
from datetime import date, time, datetime

from .program_formula import get_barber_working_intervals_for_date, get_available_slots_for_date

from services.models import Service

from appointments.models import Appointment

from django.utils import timezone


class BarberWorkingIntervalTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        
        self.barber_user = self.User.objects.create_user(
            username="barber",
            email="barber@example.com",
            password="testpass123",
            is_barber=True,
        )
        
    def test_returns_weekly_schedule_intervals_when_no_exception_exists(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="17:00:00",
            is_active=True,
        )
        
        intervals = get_barber_working_intervals_for_date(
            self.barber_user,
            date(2026, 1, 1),
        )
        
        self.assertEqual(
            intervals,
            [
                (time(9, 0), time(17, 0)),
            ],
        )
        
    def test_returns_split_intervals_when_lunch_break_exists(self):
        weekly_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="17:00:00",
            is_active=True,
        )

        LunchBreak.objects.create(
            weekly_schedule=weekly_schedule,
            start_time="12:00:00",
            end_time="13:00:00",
        )
        
        intervals = get_barber_working_intervals_for_date(
            self.barber_user,
            date(2026, 1, 1),
        )
        
        self.assertEqual(
            intervals,
            [
                (time(9, 0), time(12, 0)),
                (time(13, 0), time(17, 0)),
            ],
        )
        
    def test_if_day_off_returns_nothing(self):
        weekly_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="17:00:00",
            is_active=True
        )
        
        BarberScheduleException.objects.create(
            barber=self.barber_user,
            date=date(2026, 1, 1),
            start_time=None,
            end_time=None,
            is_day_off=True,
            reason="Test",
        )
        
        intervals = get_barber_working_intervals_for_date(
            barber=self.barber_user,
            date=date(2026, 1, 1)
        )
        
        self.assertEqual(intervals, [])
        
    def test_working_exceptions_exists_returns_intervals(self):
        weekly_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="17:00:00",
            is_active=True
        )
        
        BarberScheduleException.objects.create(
            barber=self.barber_user,
            date=date(2026, 1, 1),
            start_time="8:00:00",
            end_time="11:30:00",
            is_day_off=False,
            reason="Test",
        )
        
        BarberScheduleException.objects.create(
            barber=self.barber_user,
            date=date(2026, 1, 1),
            start_time="12:00:00",
            end_time="17:30:00",
            is_day_off=False,
            reason="Test2",
        )
        
        intervals = get_barber_working_intervals_for_date(
            barber=self.barber_user,
            date=date(2026, 1, 1),
        )
        
        self.assertEqual(
            intervals,
            [
                (time(8, 0), time(11, 30)),
                (time(12, 0), time(17, 30)),
            ],
        )
        
    def test_exception_overrides_weekly_schedule_and_lunch_break_returns_exception(self):
        weekly_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="17:00:00",
            is_active=True
        )
        
        BarberScheduleException.objects.create(
            barber=self.barber_user,
            date=date(2026, 1, 1),
            start_time="8:00:00",
            end_time="11:30:00",
            is_day_off=False,
            reason="Test",
        )
        
        LunchBreak.objects.create(
            weekly_schedule=weekly_schedule,
            start_time="12:00:00",
            end_time="13:00:00",
        )
        
        intervals = get_barber_working_intervals_for_date(
            barber=self.barber_user,
            date=date(2026, 1, 1),
        )
        
        self.assertEqual(
            intervals,
            [
                (time(8, 0), time(11, 30)),
            ]
        )
        
    def test_weekly_schedule_is_active_false_returns_nothing(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="17:00:00",
            is_active=False
        )
        
        intervals = get_barber_working_intervals_for_date(
            barber=self.barber_user,
            date=date(2026, 1, 1),
        )
        
        self.assertEqual(intervals, [])
        
class AvailableSlotsForDateTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
    
        self.barber_user = self.User.objects.create_user(
            username="barber1",
            email="barber@gmail.com",
            password="barber9980",
            is_barber=True,
        )
        
    def test_generates_slots_when_no_appointments_exist(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="10:00:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        available_slot = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service,
        )
        
        self.assertEqual(
            available_slot,
            [
                timezone.make_aware(datetime(2026, 1, 1, 9, 0)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 15)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 30)),
            ],
        )
        
    def test_slots_not_generate_outside_program(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="09:20:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        available_slot = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service,
        )
        
        self.assertEqual(available_slot, [])
        
    def test_appointment_blocks_slot_overlay(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="10:00:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        client1 = self.User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="testpass123",
        )
        
        appointment = Appointment.objects.create(
            barber=self.barber_user,
            client=client1,
            service=service,
            start_time=timezone.make_aware(datetime(2026, 1, 1, 9, 15)),
            end_time=timezone.make_aware(datetime(2026, 1, 1, 9, 45)),
        )
        
        availability = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service
        )
        
        self.assertEqual(availability, [])
        
    def test_cancelled_appointment_doesnt_block_slot(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="10:00:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        client1 = self.User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="testpass123",
        )
        
        appointment = Appointment.objects.create(
            barber=self.barber_user,
            client=client1,
            service=service,
            start_time=timezone.make_aware(datetime(2026, 1, 1, 9, 15)),
            end_time=timezone.make_aware(datetime(2026, 1, 1, 9, 45)),
            status=Appointment.Status.CANCELLED,
            notes="Test",
        )
        
        availability = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service,
        )
        
        self.assertEqual(
            availability,
            [
                timezone.make_aware(datetime(2026, 1, 1, 9, 0)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 15)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 30)),
            ]
        )
        
    def test_lunch_break_break_slots(self):
        schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="11:00:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        LunchBreak.objects.create(
            weekly_schedule=schedule,
            start_time="10:00:00",
            end_time="10:30:00",
        )
        
        availability = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service
        )
        
        self.assertEqual(
            availability,
            [
                timezone.make_aware(datetime(2026, 1 , 1, 9, 0)),
                timezone.make_aware(datetime(2026, 1 , 1, 9, 15)),
                timezone.make_aware(datetime(2026, 1 , 1, 9, 30)),
                timezone.make_aware(datetime(2026, 1 , 1, 10, 30)),
            ]
        )
        
    def test_day_off_returns_empty_list(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="11:00:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        BarberScheduleException.objects.create(
            barber=self.barber_user,
            date=date(2026, 1, 1),
            start_time=None,
            end_time=None,
            is_day_off=True,
            reason="Test",
        )
        
        availability = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service,
        )
        
        self.assertEqual(availability, [])
        
    def test_working_exception_returns_correct_slots(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="11:00:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        BarberScheduleException.objects.create(
            barber=self.barber_user,
            date=date(2026, 1, 1),
            start_time="09:00:00",
            end_time="10:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        BarberScheduleException.objects.create(
            barber=self.barber_user,
            date=date(2026, 1, 1),
            start_time="13:00:00",
            end_time="14:00:00",
            is_day_off=False,
            reason="Test",
        )
        
        availability = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service,
        )
        
        self.assertEqual(
            availability,
            [
                timezone.make_aware(datetime(2026, 1, 1, 9, 0)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 15)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 30)),
                timezone.make_aware(datetime(2026, 1, 1, 13, 0)),
                timezone.make_aware(datetime(2026, 1, 1, 13, 15)),
                timezone.make_aware(datetime(2026, 1, 1, 13, 30)),
            ]
        )
        
    def test_45_minutes_service_works_correct(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="11:00:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=45,
            price="50.00",
        )
        
        availability = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service,
        )
        
        self.assertEqual(
            availability,
            [
                timezone.make_aware(datetime(2026, 1, 1, 9, 0)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 15)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 30)),
                timezone.make_aware(datetime(2026, 1, 1, 9, 45)),
                timezone.make_aware(datetime(2026, 1, 1, 10, 0)),
                timezone.make_aware(datetime(2026, 1, 1, 10, 15)),
            ]
        )
        
    def test_more_appointments_block_slots_correct(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="11:00:00",
            is_active=True,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        client1 = self.User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="testpass123",
        )
        
        client2 = self.User.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="testpass1234",
        )
        
        appointment1 = Appointment.objects.create(
            barber=self.barber_user,
            client=client1,
            service=service,
            start_time=timezone.make_aware(datetime(2026, 1, 1, 9, 0)),
            end_time=timezone.make_aware(datetime(2026, 1, 1, 9, 30)),
            status=Appointment.Status.BOOKED,
            notes="Test",
        )
        
        appointment2 = Appointment.objects.create(
            barber=self.barber_user,
            client=client2,
            service=service,
            start_time=timezone.make_aware(datetime(2026, 1, 1, 10, 0)),
            end_time=timezone.make_aware(datetime(2026, 1, 1, 10, 30)),
            status=Appointment.Status.BOOKED,
            notes="Test",
        )
        
        availability = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service,
        )
        
        self.assertEqual(
            availability,
            [
                timezone.make_aware(datetime(2026, 1, 1, 9, 30)),
                timezone.make_aware(datetime(2026, 1, 1, 10, 30)),
            ]
        )
        
    def test_weekly_schedule_is_active_false_returns_empty_list(self):
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="11:00:00",
            is_active=False,
        )
        
        service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=30,
            price="50.00",
        )
        
        availability = get_available_slots_for_date(
            self.barber_user,
            date(2026, 1, 1),
            service,
        )
        
        self.assertEqual(availability, [])