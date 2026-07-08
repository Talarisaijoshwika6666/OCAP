from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('contests/', views.recruiter_contests, name='recruiter_contests'),
]