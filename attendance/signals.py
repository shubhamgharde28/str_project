from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkPlan, Notification
from .utils.notifications import send_realtime_notification

@receiver(post_save, sender=WorkPlan)
def workplan_notification(sender, instance, created, **kwargs):
    if created:
        users = instance.coworkers.all()

        for user in users:
            # Save DB
            Notification.objects.create(
                user=user,
                title="New Work Plan",
                message=f"Work plan scheduled on {instance.date}",
                workplan=instance
            )

            # Send realtime
            send_realtime_notification(
                user,
                "New Work Plan",
                f"Work plan scheduled on {instance.date}"
            )
