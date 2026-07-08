from django.contrib import admin
from .models import Result, CandidateAnswer

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'assessment', 'score', 'rank', 'submitted_at']
    list_filter = ['assessment', 'rank']
    search_fields = ['candidate__username', 'assessment__title']

@admin.register(CandidateAnswer)
class CandidateAnswerAdmin(admin.ModelAdmin):
    list_display = ['result', 'question', 'selected_option', 'is_correct']
    list_filter = ['is_correct']