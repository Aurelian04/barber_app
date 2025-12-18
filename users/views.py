from rest_framework import status, generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserRegisterSerializer, UserSerializer

from django.contrib.auth import get_user_model
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    
class MeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
