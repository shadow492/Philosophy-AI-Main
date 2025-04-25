from django.contrib import admin
from .models import ChatSession, ChatMessage

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'philosopher', 'summary', 'created_at', 'updated_at')
    search_fields = ('session_id', 'philosopher', 'summary')
    list_filter = ('philosopher', 'created_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'timestamp')
    search_fields = ('content',)
    list_filter = ('role', 'timestamp')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'