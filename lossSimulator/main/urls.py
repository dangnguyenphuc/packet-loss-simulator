from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="main"),
    path("api/json", views.listJsonFiles, name="listJsonFiles"),
    path("api/json/<str:filename>", views.getJson, name="getJson"),
    path("api/devices", views.getAllDevices, name="getDevices"),
    path("api/devices/<str:deviceId>/ip", views.getDeviceIps, name="getDeviceIps"),
    path("api/info", views.getInfo, name="getInfo"),
    
]
