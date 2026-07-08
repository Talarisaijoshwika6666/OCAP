from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('<int:pk>/', views.question_detail, name='question_detail'),
    path('solve/<int:pk>/', views.question_detail, name='solve_question'),
    path('run/<int:pk>/', views.run_code, name='run_code'),
    path('submit/<int:pk>/', views.submit_solution, name='submit_solution'),
    path('bookmark/<int:pk>/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
]