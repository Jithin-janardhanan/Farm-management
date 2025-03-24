# views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Farm
from .serializers import FarmSerializer
from motors.models import Motor, Valve  # Import the Motor model

class IsAdminOrManagerOrOwner(permissions.BasePermission):
    """
    Custom permission for role-based access:
    - Admins can access all farms
    - Managers can access all farms
    - Regular users can only access their own farms
    """

    def has_permission(self, request, view):
        # Allow all authenticated users to access list/create views
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow admins and managers full access
        if request.user.role in ['admin', 'manager']:
            return True
        # Regular users can only access their own farms
        return obj.owner == request.user

class FarmListCreateView(generics.ListCreateAPIView):
    """
    List all farms or create a new farm.
    Admins and managers can specify the owner, while regular users are automatically assigned as the owner.
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerOrOwner]

    def get_queryset(self):
        """
        Return all farms for admins/managers, or only user's farms for regular users.
        """
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Farm.objects.all().prefetch_related('motors')
        return Farm.objects.filter(owner=user).prefetch_related('motors')

    def perform_create(self, serializer):
        """
        Allow admins/managers to specify owner, otherwise set to current user.
        """
        user = self.request.user

        if user.role in ['admin', 'manager']:
            # Admins and managers can specify the owner
            owner_id = self.request.data.get('owner')
            if owner_id:
                # Save the farm with the specified owner
                serializer.save(owner_id=owner_id)
            else:
                # If no owner is specified, default to the current user
                serializer.save(owner=user)
        else:
            # Regular users can only create farms for themselves
            serializer.save(owner=user)

class FarmDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a farm instance
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerOrOwner]

    def get_queryset(self):
        """
        Return all farms for admins/managers, or only user's farms for regular users
        """
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Farm.objects.all().prefetch_related('motors')
        return Farm.objects.filter(owner=user).prefetch_related('motors')

class FarmMotorsView(generics.RetrieveUpdateAPIView):
    """
    View to specifically manage motors for a farm
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Farm.objects.all().prefetch_related('motors')
        return Farm.objects.filter(owner=user).prefetch_related('motors')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Only process motors field
        motor_ids = request.data.get('motors', [])

        # Update motors
        if 'motors' in request.data:
            instance.motors.set(motor_ids)

        # Use serializer for response
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class FarmMotorControlView(APIView):
    """
    API endpoint to control motors (on/off) for a specific farm.
    Only authenticated users can access this endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, farm_id, motor_id):
        """
        Handle POST requests to control a motor.
        """
        try:
            # Fetch the farm and motor
            farm = Farm.objects.get(id=farm_id)
            motor = Motor.objects.get(id=motor_id, farms=farm)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)
        except Motor.DoesNotExist:
            return Response({"error": "Motor not found in this farm"}, status=status.HTTP_404_NOT_FOUND)

        # Validate the action
        action = request.data.get('action', '').lower()
        if action not in ['on', 'off']:
            return Response(
                {"error": "Invalid action. Use 'on' or 'off'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Control all valves of the motor
        valves = Valve.objects.filter(motor=motor)
        for valve in valves:
            if action == 'on':
                valve.turn_on()
            elif action == 'off':
                valve.turn_off()

        # Return success response
        return Response({
            "status": "success",
            "message": f"All valves of motor {motor.name} turned {action}",
            "farm_id": farm.id,
            "motor_id": motor.id,
            "action": action
        })