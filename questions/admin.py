from django.contrib import admin
from .models import Question, TestCase, Bookmark

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 2

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty']
<<<<<<< HEAD
    fields = ['title', 'description', 'difficulty', 'sample_input', 'sample_output', 'hint', 'answer', 'time_limit']
    inlines = [TestCaseInline]
    
=======
    inlines = [TestCaseInline]

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'created_at']
    list_filter = ['created_at']
>>>>>>> origin/ganesh
