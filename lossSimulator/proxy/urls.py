from django.urls import path
from . import views

urlpatterns = [
    path("shape", views.proxyHandler, name="proxyHandler"),
]