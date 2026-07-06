from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('quest/', views.quest_view, name='quest'),
    path('explore/', views.explore_view, name='explore'),
    path('study-plan/', views.study_plan_view, name='study_plan'),
]