from django.urls import path
from . import views

urlpatterns = [
    path("api/json", views.listJsonFiles, name="listJsonFiles"),
    path("api/json/<str:filename>", views.getJson, name="getJson"),
    path("api/devices", views.getAllDevices, name="getDevices"),
    path("api/ip/<str:deviceId>", views.getDeviceIps, name="getDeviceIps"),
    path("api/info", views.getInfo, name="getInfo"),
    path("api/run", views.runZrtcAndroidApp, name="runZrtcAndroidApp"),
    path("api/run/<str:taskId>", views.runTaskHandler, name="runTaskHandler"),
    path("api/file/<str:folderName>", views.fileHanldler, name="fileHanldler"),
    path("api/stat", views.statHandler, name="statHandler"),
]
