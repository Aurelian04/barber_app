from django.conf import settings
from django.db import models
from django.utils import timezone


class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    barber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="barber_appointments",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_appointments",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.BOOKED,
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-start_time",)
        indexes = [
            models.Index(fields=["barber", "start_time"]),
            models.Index(fields=["client", "start_time"]),
        ]

    def __str__(self):
        return f"{self.start_time} - {self.service} ({self.client} -> {self.barber})"
