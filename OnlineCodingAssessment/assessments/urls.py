from django.urls import path
from . import views

urlpatterns = [
    path('', views.assessment_list, name='assessments'),
    path('<int:pk>/', views.assessment_detail, name='assessment_detail'),
    path('<int:pk>/take/', views.take_assessment, name='take_assessment'),
]