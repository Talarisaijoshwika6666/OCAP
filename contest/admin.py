from django.contrib import admin
from .models import Contest, ContestRegistration
 
 
@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'is_active', 'problem_count')
    filter_horizontal = ('questions',)
    search_fields = ('title',)
    list_filter = ('is_active',)
 
    def problem_count(self, obj):
        return obj.questions.count()
 
 
@admin.register(ContestRegistration)
class ContestRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'contest', 'registered_at')
    list_filter = ('contest',)
 