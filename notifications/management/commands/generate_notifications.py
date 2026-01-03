from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

from attendance.models import WorkPlan, DailySummaryReport
from django.contrib.contenttypes.models import ContentType

from notifications.models import Notification


class Command(BaseCommand):
    help = 'Generate notifications for today from WorkPlan and DailySummaryReport follow-up dates'

    def handle(self, *args, **options):
        today = date.today()
        created = 0

        # WorkPlan notifications: notify created_by and coworkers when workplan.date == today
        wplans = WorkPlan.objects.filter(date=today)
        ct_wp = ContentType.objects.get_for_model(WorkPlan)
        for wp in wplans:
            titles = ', '.join([t.title for t in wp.titles.all()])
            message = f"You have workplan today: {titles or 'Workplan'}"

            recipients = list(wp.coworkers.all())
            if wp.created_by not in recipients:
                recipients.append(wp.created_by)

            for user in recipients:
                # avoid duplicate identical notification for same user/object
                obj, created_flag = Notification.objects.get_or_create(
                    user=user,
                    notify_date=today,
                    content_type=ct_wp,
                    object_id=wp.id,
                    defaults={'message': message, 'metadata': {'workplan_id': wp.id}}
                )
                if created_flag:
                    created += 1

        # DailySummaryReport follow_up_date notifications: notify the report owner
        dsrs = DailySummaryReport.objects.filter(follow_up_date=today)
        ct_dsr = ContentType.objects.get_for_model(DailySummaryReport)
        for dsr in dsrs:
            message = f"You have a follow-up today: {dsr.summary_text[:120]}"
            user = dsr.user
            obj, created_flag = Notification.objects.get_or_create(
                user=user,
                notify_date=today,
                content_type=ct_dsr,
                object_id=dsr.id,
                defaults={'message': message, 'metadata': {'daily_summary_id': dsr.id}}
            )
            if created_flag:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Notifications generated: {created}'))
