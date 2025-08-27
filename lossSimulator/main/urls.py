from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="main"),
    path("api/json", views.listJsonFiles, name="listJsonFiles"),
    path("api/json/<str:filename>", views.getJson, name="getJson"),
    path("api/ip", views.getAllDevices, name="getIps"),
    path("api/devices", views.getDeviceNumbers, name="getDeviceNumbers")
]
