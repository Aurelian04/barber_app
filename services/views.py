from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet


from .permissions import IsBarber
from .models import Service
from .serializers import ServiceSerializer


class ServiceViewList(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Service.objects.filter(is_active=True).select_related("barber").order_by("name")
        barber_id = self.request.query_params.get("barber")
        if barber_id:
            qs = qs.filter(barber_id=barber_id)
        return qs



class BarberServiceViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsBarber]

    def get_queryset(self):
        return Service.objects.filter(barber=self.request.user).order_by("name")

    def perform_create(self, serializer):
        serializer.save(barber=self.request.user)
