from rest_framework import serializers

from .models import BarberWeeklySchedule, LunchBreak, BarberScheduleException 



class BarberScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarberWeeklySchedule
        fields = [
            "id",
            "barber",
            "weekday",
            "start_time",
            "end_time",
            "is_active",
        ]
        read_only_fields = ["id", "barber", "is_active"]