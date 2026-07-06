from django.contrib import admin
from .models import Assessment, Question, TestCase

admin.site.register(Assessment)
admin.site.register(Question)
admin.site.register(TestCase)