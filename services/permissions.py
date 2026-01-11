from rest_framework.permissions import BasePermission

class IsBarberOrStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (user.is_barber or user.is_staff)
        )
