# urls.py
from django.urls import path
from .views import (
    MotorListCreateView,
    MotorRetrieveUpdateDestroyView,
    ValveListView,
    ValveAddView,
    ValveControlView,
    ValveStatusView,  motor_management
)

urlpatterns = [
    # Motor endpoints
    path('motors/', MotorListCreateView.as_view(), name='motor-list-create'),
    path('motors/<int:pk>/', MotorRetrieveUpdateDestroyView.as_view(), name='motor-detail'),

    # Valve endpoints
    path('motors/<int:motor_id>/valves/', ValveListView.as_view(), name='valve-list'),
    path('motors/<int:motor_id>/add-valve/', ValveAddView.as_view(), name='add-valve'),
    path('motors/<int:motor_id>/control-valve/<int:valve_number>/', ValveControlView.as_view(), name='control-valve'),
    path('motors/<int:motor_id>/valve-status/', ValveStatusView.as_view(), name='valve-status'),


    path('motor-management/', motor_management, name='motor_management'),
]