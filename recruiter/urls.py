from django.urls import path
from . import views

urlpatterns = [
    path('', views.recruiter_dashboard, name='recruiter_dashboard'),
]