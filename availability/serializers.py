from rest_framework import serializers

from .models import BarberWeeklySchedule, LunchBreak, BarberScheduleException 



class BarberWeeklyScheduleSerializer(serializers.ModelSerializer):
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
        read_only_fields = ["id", "barber"]
        
    def validate(self, attrs):
        request = self.context.get("request")
        
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")
        
        if not request.user.is_barber:
            raise serializers.ValidationError("Only barbers can manage weekly schedules.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data["barber"] = self.context["request"].user
        return super().create(validated_data)
    
    
class LunchBreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = LunchBreak
        fields = [
            "id",
            "weekly_schedule",
            "start_time",
            "end_time",
        ]
        
    def validate(self, attrs):
        request = self.context.get("request")
        
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")
        
        if not request.user.is_barber:
            raise serializers.ValidationError("Only barbers can manage lunch breaks.")
        
        weekly_schedule = attrs.get(
        "weekly_schedule",
        self.instance.weekly_schedule if self.instance else None
    )
        
        if weekly_schedule.barber != request.user:
            raise serializers.ValidationError(
                {"weekly_schedule": "You can only add a lunch break to your own weekly schedule."}
            )
        
        return attrs
    
class BarberScheduleExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarberScheduleException
        fields = [
            "id",
            "barber",
            "date",
            "start_time",
            "end_time",
            "is_day_off",
            "reason",
        ]
        read_only_fields = ["id", "barber"]
        
    def validate(self, attrs):
        request = self.context.get("request")
        
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")
        
        if not request.user.is_barber:
            raise serializers.ValidationError("Only barbers can modify their schedule.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data["barber"] = self.context["request"].user
        return super().create(validated_data)