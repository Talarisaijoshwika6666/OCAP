from django.contrib import admin
from .models import Topic, TopicProgress
admin.site.register(Topic)


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject_slug', 'topic_slug', 'status', 'updated_at')
    list_filter = ('status', 'subject_slug')
    search_fields = ('user__username', 'subject_slug', 'topic_slug')