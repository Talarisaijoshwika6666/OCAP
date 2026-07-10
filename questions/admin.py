from django.contrib import admin
from .models import Question, TestCase, Bookmark, QuestionLanguage

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 2

class QuestionLanguageInline(admin.TabularInline):
    """
    Lets a recruiter/admin pick a language from a dropdown and type the
    reference answer for that language, right below the general Answer
    field. The candidate is shown whichever of these matches the language
    they were coding in once they hit 3 wrong attempts; if nothing is set
    for their language, the general Answer field is used instead.
    """
    model = QuestionLanguage
    extra = 1
    fields = ['language', 'answer']
    verbose_name = "Language-specific answer"
    verbose_name_plural = "Language-specific answers"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty']
    fields = ['title', 'description', 'difficulty', 'sample_input', 'sample_output', 'hint', 'answer', 'time_limit']
    inlines = [QuestionLanguageInline, TestCaseInline]

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'is_hidden']
    list_filter = ['is_hidden', 'question']
    search_fields = ['question__title']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'created_at']
    list_filter = ['created_at']
