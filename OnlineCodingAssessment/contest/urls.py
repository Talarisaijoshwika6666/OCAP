from django.urls import path
from . import views

urlpatterns = [
    path('', views.contest_view, name='contest'),
    path('register/<int:pk>/', views.register_contest, name='register_contest'),
]