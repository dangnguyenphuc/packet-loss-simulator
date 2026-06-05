from django.urls import path
from . import views

urlpatterns = [
    path("shape", views.proxy_handler, name="proxy_handler"),
]
