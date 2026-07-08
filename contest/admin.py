from django.contrib import admin
from .models import Contest, ContestRegistration, ContestMCQ, ContestMCQAnswer
 
 
class ContestMCQInline(admin.TabularInline):
    model = ContestMCQ
    extra = 0


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'start_time', 'end_time', 'is_active', 'problem_count', 'mcq_count')
    filter_horizontal = ('questions',)
    search_fields = ('title',)
    list_filter = ('is_active',)
    inlines = [ContestMCQInline]
 
    def problem_count(self, obj):
        return obj.questions.count()
 
 
@admin.register(ContestRegistration)
class ContestRegistrationAdmin(admin.ModelAdmin):
    # violation_count / auto_submitted surface proctoring activity
    # directly in the admin so recruiters can audit flagged candidates.
    list_display = ('user', 'contest', 'registered_at', 'violation_count', 'auto_submitted', 'auto_submitted_at')
    list_filter = ('contest', 'auto_submitted')
 

@admin.register(ContestMCQ)
class ContestMCQAdmin(admin.ModelAdmin):
    list_display = ('contest', 'question_text', 'correct_option', 'marks', 'difficulty')
    list_filter = ('contest', 'difficulty')


@admin.register(ContestMCQAnswer)
class ContestMCQAnswerAdmin(admin.ModelAdmin):
    list_display = ('mcq', 'user', 'selected_option', 'is_correct', 'answered_at')
    list_filter = ('is_correct',)
