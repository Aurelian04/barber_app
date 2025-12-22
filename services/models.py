from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
