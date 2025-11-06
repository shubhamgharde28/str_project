# attendance/utils.py

from .models import ActivityLog

def log_activity(user, action, entity, description="", ip_address=None):
    ActivityLog.objects.create(
        user=user,
        action=action,
        entity=entity,
        description=description,
        ip_address=ip_address,
    )
