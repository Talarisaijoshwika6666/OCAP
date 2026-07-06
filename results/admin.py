from django.contrib import admin
from .models import Result

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'assessment', 'score', 'rank', 'submitted_at']
    list_filter = ['assessment', 'rank']
    search_fields = ['candidate__username', 'assessment__title']