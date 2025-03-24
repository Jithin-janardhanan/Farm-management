# urls.py
from tempfile import template

from django.urls import path
from django.views.generic import TemplateView

from .views import FarmListCreateView, FarmDetailView, FarmMotorsView, FarmMotorControlView

urlpatterns = [
    path('farms/', FarmListCreateView.as_view(), name='farm-list-create'),
    path('farms/<int:pk>/', FarmDetailView.as_view(), name='farm-detail'),
    path('farms/<int:pk>/motors/', FarmMotorsView.as_view(), name='farm-motors'),
path('farms/<int:farm_id>/motors/<int:motor_id>/control/', FarmMotorControlView.as_view(), name='farm-motor-control'),
    path('create-farm/',TemplateView.as_view(template_name ='create_farm.html'),name='create_farm_page'),
]