# farm/views.py
from rest_framework import generics
from .models import Farm, Motor, Valve
from .serializers import FarmSerializer, MotorSerializer, ValveSerializer

class FarmListCreateView(generics.ListCreateAPIView):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer

class FarmDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer

class MotorListCreateView(generics.ListCreateAPIView):
    queryset = Motor.objects.all()
    serializer_class = MotorSerializer

class MotorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Motor.objects.all()
    serializer_class = MotorSerializer

class ValveListCreateView(generics.ListCreateAPIView):
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer

class ValveDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer