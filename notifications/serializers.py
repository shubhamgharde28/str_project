from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    # For superusers, allow seeing/setting the target user id
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_id', 'user_email', 'message', 'notify_date', 'is_read', 'created_at', 'metadata']
        read_only_fields = ['id', 'created_at', 'user_id', 'user_email']
