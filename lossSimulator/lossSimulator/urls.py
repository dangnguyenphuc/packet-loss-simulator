from django.contrib import admin
from django.urls import path, include, re_path
from main.views.spa_view import SpaView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('api/proxy/', include("proxy.urls")),
    re_path(r'^(?!api/|static/|admin/).*$', SpaView.as_view()),
]
