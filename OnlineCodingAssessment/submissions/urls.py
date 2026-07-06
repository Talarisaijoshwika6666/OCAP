from django.urls import path
from . import views

urlpatterns = [
    path('submit/<int:question_id>/', views.submit_code, name='submit_code'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
]