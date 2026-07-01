from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers


from .models import Appointment
from services.models import Service



class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "barber",
            "client",
            "service",
            "start_time",
            "end_time",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "end_time", "status", "created_at", "updated_at", "client"]
        
    def validate(self, attrs):
        """
        Business rules:
        - barber must be is_barber=True
        - client is current user (set in view via perform_create)
        - service must belong to barber
        - compute end_time from service.duration_minutes
        - prevent overlap for barber (only BOOKED appointments block)
        """
        barber = attrs.get("barber")
        service = attrs.get("service")
        start_time = attrs.get("start_time")
                
        if not barber:
            raise serializers.ValidationError({"barber": "Barber is required."})
                
        if not getattr(barber, "is_barber", False):
            raise serializers.ValidationError({"barber": "Selected user is not a barber."})
                
        if not service:
            raise serializers.ValidationError({"service": "Service is required."})
                
                
        if service.barber_id != barber.id:
            raise serializers.ValidationError({"service": "This service does not belong to the selected barber."})
                
        if not start_time:
            raise serializers.ValidationError({"start_time": "Start time is required."})
                
        if timezone.is_aware(start_time) and start_time < timezone.now():
            raise serializers.ValidationError({"start_time": "Start time must be in the future."})
                
        end_time = start_time + timedelta(minutes=service.duration_minutes)
                
                
        qs = Appointment.objects.filter(
            barber = barber,
            status = Appointment.Status.BOOKED,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
                
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
                    
        if qs.exists():
            raise serializers.ValidationError({"start_time": "This time slot overlaps with another appointment."})
                
        attrs["end_time"] = end_time
        return attrs