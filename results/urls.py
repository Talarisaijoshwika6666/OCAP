from django.urls import path
from . import views
 
urlpatterns = [
    path('take/<int:assessment_id>/', views.take_test, name='take_test'),
    path('take/<int:assessment_id>/run/<int:question_id>/', views.run_sample, name='run_sample'),
    path('submit/<int:assessment_id>/', views.submit_test, name='submit_test'),
    path('result/<int:result_id>/', views.result_detail, name='result_detail'),
    path('my-results/', views.my_results, name='my_results'),
]