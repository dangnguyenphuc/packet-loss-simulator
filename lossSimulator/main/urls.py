from django.urls import path
from .views import (
    JsonFileListView,
    JsonFileDetailView,
    DeviceListView,
    DeviceIpView,
    InfoView,
    TaskRunView,
    TaskDetailView,
    FileView,
    StatView,
)

urlpatterns = [
    path("api/json", JsonFileListView.as_view(), name="list_json_files"),
    path("api/json/<str:filename>", JsonFileDetailView.as_view(), name="get_json"),
    path("api/devices", DeviceListView.as_view(), name="device-list"),
    path("api/devices/<str:device_id>/ip", DeviceIpView.as_view(), name="device-ips"),
    path("api/info", InfoView.as_view(), name="info"),
    path("api/devices/<str:device_id>/<str:type>", TaskRunView.as_view(), name="task"),
    path("api/tasks/<str:task_id>", TaskDetailView.as_view(), name="task-detail"),
    path("api/files/<str:folder_name>", FileView.as_view(), name="file-handler"),
    path("api/stats", StatView.as_view(), name="stats"),
]
