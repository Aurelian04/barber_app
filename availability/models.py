from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class BarberWeeklySchedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 1, "Monday"
        TUESDAY = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY = 4, "Thursday"
        FRIDAY = 5, "Friday"
        SATURDAY = 6, "Saturday"
        SUNDAY = 7, "Sunday"

    barber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="weekly_schedules",
        limit_choices_to={"is_barber": True},
    )
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["barber", "weekday", "start_time"]
        constraints = [
            models.CheckConstraint(
                condition=Q(start_time__lt=F("end_time")),
                name="weekly_schedule_start_before_end",
            ),
            models.UniqueConstraint(
                fields=["barber", "weekday", "start_time", "end_time"],
                name="unique_weekly_schedule_interval_per_barber",
            ),
        ]

    def clean(self):
        super().clean()

        if not self.barber_id:
            raise ValidationError({"barber": "Barber is required."})

        if not self.barber.is_barber:
            raise ValidationError({"barber": "Selected user must be a barber."})

        overlapping_intervals = BarberWeeklySchedule.objects.filter(
            barber=self.barber,
            weekday=self.weekday,
            is_active=True,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )

        if self.pk:
            overlapping_intervals = overlapping_intervals.exclude(pk=self.pk)

        if overlapping_intervals.exists():
            raise ValidationError(
                {
                    "non_field_errors": [
                        "This weekly schedule overlaps with another interval for the same day."
                    ]
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.barber.username} | "
            f"{self.get_weekday_display()} | "
            f"{self.start_time} - {self.end_time}"
        )


class BarberScheduleException(models.Model):
    barber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schedule_exceptions",
        limit_choices_to={"is_barber": True},
    )
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_day_off = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["barber", "date", "start_time"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(is_day_off=True, start_time__isnull=True, end_time__isnull=True)
                    | Q(
                        is_day_off=False,
                        start_time__isnull=False,
                        end_time__isnull=False,
                    )
                ),
                name="schedule_exception_valid_shape",
            ),
            models.CheckConstraint(
                condition=Q(is_day_off=True) | Q(start_time__lt=F("end_time")),
                name="schedule_exception_start_before_end",
            ),
        ]

    def clean(self):
        super().clean()

        if not self.barber_id:
            raise ValidationError({"barber": "Barber is required."})

        if not self.barber.is_barber:
            raise ValidationError({"barber": "Selected user must be a barber."})

        same_day_exceptions = BarberScheduleException.objects.filter(
            barber=self.barber,
            date=self.date,
        )

        if self.pk:
            same_day_exceptions = same_day_exceptions.exclude(pk=self.pk)

        if self.is_day_off:
            if self.start_time is not None or self.end_time is not None:
                raise ValidationError(
                    {
                        "non_field_errors": [
                            "A day-off exception cannot have start_time or end_time."
                        ]
                    }
                )

            if same_day_exceptions.exists():
                raise ValidationError(
                    {
                        "non_field_errors": [
                            "A day-off exception cannot coexist with other exception intervals on the same date."
                        ]
                    }
                )
        else:
            if self.start_time is None or self.end_time is None:
                raise ValidationError(
                    {
                        "non_field_errors": [
                            "A working exception must have both start_time and end_time."
                        ]
                    }
                )

            if same_day_exceptions.filter(is_day_off=True).exists():
                raise ValidationError(
                    {
                        "non_field_errors": [
                            "Cannot add working intervals on a date marked as day off."
                        ]
                    }
                )

            overlapping_intervals = same_day_exceptions.filter(
                is_day_off=False,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            )

            if overlapping_intervals.exists():
                raise ValidationError(
                    {
                        "non_field_errors": [
                            "This exception interval overlaps with another exception interval on the same date."
                        ]
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.is_day_off:
            return f"{self.barber.username} | {self.date} | DAY OFF"

        return (
            f"{self.barber.username} | "
            f"{self.date} | "
            f"{self.start_time} - {self.end_time}"
        )
        

class LunchBreak(models.Model):
    weekly_schedule = models.OneToOneField(
        BarberWeeklySchedule,
        on_delete=models.CASCADE,
        related_name="lunch_break",
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["weekly_schedule", "start_time"]
        constraints = [
            models.CheckConstraint(
                condition=Q(start_time__lt=F("end_time")),
                name="lunch_break_start_before_end",
            ),
        ]

    def clean(self):
        super().clean()

        if not self.weekly_schedule_id:
            raise ValidationError({"weekly_schedule": "Weekly schedule is required."})

        if not self.weekly_schedule.is_active:
            raise ValidationError(
                {"weekly_schedule": "Cannot add a lunch break to an inactive schedule."}
            )

        if self.start_time < self.weekly_schedule.start_time:
            raise ValidationError(
                {"start_time": "Lunch break cannot start before the working schedule starts."}
            )

        if self.end_time > self.weekly_schedule.end_time:
            raise ValidationError(
                {"end_time": "Lunch break cannot end after the working schedule ends."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.weekly_schedule.barber.username} | "
            f"{self.weekly_schedule.get_weekday_display()} | "
            f"{self.start_time} - {self.end_time}"
        )