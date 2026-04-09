from rest_framework.viewsets import ModelViewSet

from .serializers import BarberWeeklyScheduleSerializer, LunchBreakSerializer, BarberScheduleExceptionSerializer
from.permissions import IsBarberOrStaff
from .models import BarberWeeklySchedule, BarberScheduleException, LunchBreak


class BarberWeeklyScheduleViewSet(ModelViewSet):
    serializer_class = BarberWeeklyScheduleSerializer
    permission_classes = [IsBarberOrStaff]
    
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return BarberWeeklySchedule.objects.all()

        return BarberWeeklySchedule.objects.filter(barber=user)
    
class BarberScheduleExceptionViewSet(ModelViewSet):
    serializer_class = BarberScheduleExceptionSerializer
    permission_classes = [IsBarberOrStaff]
    
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return BarberScheduleException.objects.all()

        return BarberScheduleException.objects.filter(barber=user)
    
class LunchBreakViewSet(ModelViewSet):
    serializer_class = LunchBreakSerializer
    permission_classes = [IsBarberOrStaff]
    
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return LunchBreak.objects.all()

        return LunchBreak.objects.filter(weekly_schedule__barber=user)