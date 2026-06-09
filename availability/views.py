from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from .serializers import BarberWeeklyScheduleSerializer, LunchBreakSerializer, BarberScheduleExceptionSerializer, AvailableSlotsSerializer
from.permissions import IsBarberOrStaff
from .models import BarberWeeklySchedule, BarberScheduleException, LunchBreak
from .program_formula import get_available_slots_for_date


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
    

class AvailableSlotsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        serializer = AvailableSlotsSerializer(
            data=request.query_params
        )
        
        serializer.is_valid(raise_exception=True)
        
        barber = serializer.validated_data["barber"]
        service = serializer.validated_data["service"]
        date = serializer.validated_data["date"]
        
        slots = get_available_slots_for_date(
            barber,
            date,
            service,
        )
        
        slots_data = [slot.isoformat() for slot in slots]
        
        return Response({"slots": slots_data})