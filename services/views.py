from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from .serializers import ServiceSerializer
from .models import Service


class ServiceViewList(generics.ListAPIView):
    
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by("name")
    
    
class ServiceAdminViewSet(ModelViewSet):
    
    queryset = Service.objects.all().order_by("name")
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAdminUser]