from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notify_date = models.DateField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # optional generic relation to related object (WorkPlan / DailySummaryReport)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-notify_date', '-created_at']

    def __str__(self):
        return f"Notification to {self.user.email} on {self.notify_date}: {self.message[:50]}"
