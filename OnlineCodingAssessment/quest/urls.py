from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('study-plan/<str:topic>/', views.study_plan_view, name='study_plan'),
]