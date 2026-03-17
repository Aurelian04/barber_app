from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from appointments.models import Appointment
from services.models import Service



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
        
        payload = {
            "barber": self.barber_user.id,
            "service": self.service.id,
            "start_time": (timezone.now() + timedelta(days=1)).isoformat(),
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