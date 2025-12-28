from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import WorkDetail, Notification
from attendance.utils.notifications import send_realtime_notification

class Command(BaseCommand):
    help = "Follow-up reminders"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        followups = WorkDetail.objects.filter(
            next_followup_date=today
        )

        for obj in followups:
            user = obj.hourly_report.user

            Notification.objects.create(
                user=user,
                title="Follow-up Reminder",
                message=f"Follow-up today for {obj.customer_name}",
                work_detail=obj
            )

            send_realtime_notification(
                user,
                "Follow-up Reminder",
                f"Follow-up today for {obj.customer_name}"
            )
