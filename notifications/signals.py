from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from datetime import date
from django.contrib.contenttypes.models import ContentType

from attendance.models import WorkPlan, DailySummaryReport
from .models import Notification


def _create_notification_if_needed(user, message, notify_date, content_obj, metadata=None):
    if not user:
        return False
    ct = ContentType.objects.get_for_model(content_obj.__class__)
    obj, created = Notification.objects.get_or_create(
        user=user,
        notify_date=notify_date,
        content_type=ct,
        object_id=content_obj.id,
        defaults={
            'message': message,
            'metadata': metadata or {}
        }
    )
    return created


@receiver(post_save, sender=WorkPlan)
def workplan_post_save(sender, instance: WorkPlan, created, **kwargs):
    """When a WorkPlan is created or updated, if its `date` equals today, create notifications
    for the creator and coworkers."""
    try:
        today = date.today()
        if instance.date == today:
            # build a simple message; titles may not be available if m2m set later
            titles = ', '.join([t.title for t in instance.titles.all()]) if instance.titles.exists() else 'Workplan'
            message = f"You have workplan today: {titles}"

            recipients = list(instance.coworkers.all())
            if instance.created_by and instance.created_by not in recipients:
                recipients.append(instance.created_by)

            for user in recipients:
                _create_notification_if_needed(user, message, today, instance, metadata={'workplan_id': instance.id})
    except Exception:
        # keep signals safe — don't raise
        return


@receiver(m2m_changed, sender=WorkPlan.coworkers.through)
def workplan_coworkers_changed(sender, instance: WorkPlan, action, pk_set, **kwargs):
    """When coworkers are added to a WorkPlan whose date is today, create notifications for those users."""
    try:
        if action == 'post_add' and instance.date == date.today():
            titles = ', '.join([t.title for t in instance.titles.all()]) if instance.titles.exists() else 'Workplan'
            message = f"You have workplan today: {titles}"
            for uid in pk_set:
                try:
                    user = instance.coworkers.model.objects.get(pk=uid)
                    _create_notification_if_needed(user, message, instance.date, instance, metadata={'workplan_id': instance.id})
                except Exception:
                    continue
    except Exception:
        return


@receiver(post_save, sender=DailySummaryReport)
def dailysummary_post_save(sender, instance: DailySummaryReport, created, **kwargs):
    """When a DailySummaryReport is created/updated and `follow_up_date` equals today, notify the report user."""
    try:
        if instance.follow_up_date and instance.follow_up_date == date.today():
            message = f"You have a follow-up today: {instance.summary_text[:120]}"
            _create_notification_if_needed(instance.user, message, instance.follow_up_date, instance, metadata={'daily_summary_id': instance.id})
    except Exception:
        return
