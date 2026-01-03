from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notify_date', 'is_read', 'created_at')
    list_filter = ('is_read', 'notify_date')
    search_fields = ('user__email', 'message')
