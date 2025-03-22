# urls.py
from django.urls import path
from django.views.generic import TemplateView

from .views import (
    MotorListCreateView,
    MotorRetrieveUpdateDestroyView,
    ValveListView,
    ValveAddView,
    ValveControlView,
    ValveStatusView,
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


    path('motor-managment/', TemplateView.as_view(template_name="motor_managment.html"), name='motor_management'),

]