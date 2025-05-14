from django.urls import path
from .views import dashboard_view, upload_json

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('upload/', upload_json, name='upload_json'),
]
