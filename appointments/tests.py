from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from appointments.models import Appointment
from services.models import Service
from availability.models import BarberWeeklySchedule



class AppointmentApiTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        
        self.client_user = self.User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
        )
        
        self.barber_user = self.User.objects.create_user(
            username="barber",
            email="barber@example.com",
            password="testpass123",
            is_barber=True,
        )
        
        self.service = Service.objects.create(
            barber=self.barber_user,
            name="Tuns",
            duration_minutes=45,
            price=50,
        )
        
    def test_client_can_create_appointment(self):
        self.client.force_authenticate(user=self.client_user)
        
        weekly_schedule = BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=4,
            start_time="09:00:00",
            end_time="11:00:00",
            is_active=True,
        )
        
        payload = {
            "barber": self.barber_user.id,
            "service": self.service.id,
            "start_time": timezone.make_aware(datetime(2026, 12, 3, 9, 15)).isoformat(),
            "notes": "Test appointment",
        }
        
        url = "/api/appointments/"
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.client, self.client_user)
        self.assertEqual(appointment.barber, self.barber_user)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.status, Appointment.Status.BOOKED)
        
    def test_client_can_cancel_booked_appointment(self):
        appointment = Appointment.objects.create(
            barber=self.barber_user,
            client=self.client_user,
            service=self.service,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=45),
            status=Appointment.Status.BOOKED,
            notes="Test cancel",
        )
        
        self.client.force_authenticate(user=self.client_user)
        
        response = self.client.post(f"/api/appointments/{appointment.id}/cancel/")
        
        appointment.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)
        
    def test_barber_cannot_complete_cancelled_appointment(self):
        appointment = Appointment.objects.create(
            barber=self.barber_user,
            client=self.client_user,
            service=self.service,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=45),
            status=Appointment.Status.CANCELLED,
            notes="Alerady cancelled",
        )
        
        self.client.force_authenticate(user=self.barber_user)
        
        response = self.client.post(f"/api/barber/appointments/{appointment.id}/complete/")
        
        appointment.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)
        
    def test_client_can_not_cancel_another_client_appointment(self):
        client1 = self.User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="testpass123",
        )
        
        client2 = self.User.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="testpass123",
        )
        
        appointment = Appointment.objects.create(
            barber=self.barber_user,
            client=client1,
            service=self.service,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=45),
            status=Appointment.Status.BOOKED,
            notes="Tuns",
        )
        
        self.client.force_authenticate(user=client2)
        
        response = self.client.post(f"/api/appointments/{appointment.id}/cancel/")
        
        appointment.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(appointment.status, Appointment.Status.BOOKED)
        
    def test_barber_cannot_complete_another_barber_appointment(self):
        barber1 = self.User.objects.create_user(
            username="barber1",
            email="barber1@gmail.com",
            password="testpass123",
            is_barber=True
        )
        
        barber2 = self.User.objects.create_user(
            username="barber2",
            email="barber2@gamil.com",
            password="testpass123",
            is_barber=True,
        )
        
        service1 = Service.objects.create(
            barber=barber1,
            name="Tuns barber1",
            duration_minutes=45,
            price=50,
        )
        
        appointment = Appointment.objects.create(
            barber=barber1,
            client=self.client_user,
            service=service1,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=45),
            status=Appointment.Status.BOOKED,
            notes="Tuns",
        )
        
        
        self.client.force_authenticate(user=barber2)
        
        response = self.client.post(f"/api/barber/appointments/{appointment.id}/complete/")
        
        appointment.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(appointment.status, Appointment.Status.BOOKED)
        
    def test_client_cannot_create_appointment_if_service_belongs_to_another_barber(self):
        barber1 = self.User.objects.create_user(
            username="barber1",
            email="barber1@gmail.com",
            password="testpass123",
            is_barber=True
        )
        
        barber2 = self.User.objects.create_user(
            username="barber2",
            email="barber2@gamil.com",
            password="testpass123",
            is_barber=True,
        )
        
        service1 = Service.objects.create(
            barber=barber1,
            name="Tuns barber1",
            duration_minutes=45,
            price=50,
        )
        
        payload = {
            "barber": barber2.id,
            "service": service1.id,
            "start_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "notes": "Test"
            }
        
        self.client.force_authenticate(user=self.client_user)
        
        response = self.client.post(f"/api/appointments/", payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Appointment.objects.count(), 0)
        
    def test_appointment_cannot_overlap_with_another_one(self):
        client1 = self.User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="testpass123",
        )
        
        client2 = self.User.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="testpass123",
        )
        
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=45)
        
        appointment1 = Appointment.objects.create(
            barber=self.barber_user,
            client=client1,
            service=self.service,
            start_time=start_time,
            end_time=end_time,
            status=Appointment.Status.BOOKED,
            notes="Tuns",
        )
        
        payload = {
            "barber": self.barber_user.id,
            "service": self.service.id,
            "start_time": start_time.isoformat(),
            "notes": "Test"
            
        }
        
        self.client.force_authenticate(user = client2)
        
        response = self.client.post(f"/api/appointments/", payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Appointment.objects.count(), 1)
        
    def test_appointment_can_overlap_with_existing_cancelld_one(self):
        client1 = self.User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="testpass123",
        )
        
        client2 = self.User.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="testpass123",
        )
        
        BarberWeeklySchedule.objects.create(
            barber=self.barber_user,
            weekday=2,
            start_time="09:00:00",
            end_time="11:00:00",
            is_active=True,
        )
        
        start_time = timezone.make_aware(datetime(2026, 12, 1, 9, 15))
        
        appointment1 = Appointment.objects.create(
            barber=self.barber_user,
            client=client1,
            service=self.service,
            start_time=start_time,
            end_time=timezone.make_aware(datetime(2026, 12, 1, 10, 0)),
            status=Appointment.Status.CANCELLED,
            notes="Tuns",
        )
        
        payload = {
            "barber": self.barber_user.id,
            "service": self.service.id,
            "start_time": start_time.isoformat(),
            "notes": "Test"
            
        }
        
        self.client.force_authenticate(user = client2)
        
        response = self.client.post(f"/api/appointments/", payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)
        
    def test_client_see_only_his_appointment(self):
        client1 = self.User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="testpass123",
        )
        
        client2 = self.User.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="testpass123",
        )
        
        appointment1 = Appointment.objects.create(
            barber=self.barber_user,
            client=client1,
            service=self.service,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=45),
            status=Appointment.Status.CANCELLED,
            notes="Tuns",
        )
        appointment2 = Appointment.objects.create(
            barber=self.barber_user,
            client=client2,
            service=self.service,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=45),
            status=Appointment.Status.CANCELLED,
            notes="Tuns",
        )
        
        self.client.force_authenticate(user=client2)
        
        response = self.client.get(f"/api/appointments/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["client"], client2.id)