from django.urls import path
from .views import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    # path('upload/', upload_json, name='upload_json'),
    # path('delete_documents/<str:ticker>/', delete_equity_documents, name='delete_equity_documents'),

]
