from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet

from .serializers import AppointmentSerializer
from .models import Appointment


class ClientAppointmentView(ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        user = self.request.user
        return Appointment.objects.filter(client=user)
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)