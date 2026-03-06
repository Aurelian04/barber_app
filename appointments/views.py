from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin

from .serializers import AppointmentSerializer
from .models import Appointment


class ClientAppointmentViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status != Appointment.Status.BOOKED:
            return Response(
                {"detail": "Only booked appointments can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])

        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BarberAppointmentViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """Barber sees only his appointments and can cancel/complete them."""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_barber:
            return Appointment.objects.none()
        return Appointment.objects.filter(barber=user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status != Appointment.Status.BOOKED:
            return Response(
                {"detail": "Only booked appointments can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])

        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status != Appointment.Status.BOOKED:
            return Response(
                {"detail": "Only booked appointments can be completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = Appointment.Status.COMPLETED
        appointment.save(update_fields=["status", "updated_at"])

        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)