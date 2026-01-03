from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Superusers see all notifications; normal users only their own
        qs = Notification.objects.all().order_by('-notify_date', '-created_at') if (self.request.user and self.request.user.is_superuser) else Notification.objects.filter(user=self.request.user).order_by('-notify_date', '-created_at')

        # Filtering by query params
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() in ['true', '1']:
                qs = qs.filter(is_read=True)
            elif is_read.lower() in ['false', '0']:
                qs = qs.filter(is_read=False)

        user_id = self.request.query_params.get('user')
        if user_id and self.request.user.is_superuser:
            try:
                uid = int(user_id)
                qs = qs.filter(user__id=uid)
            except ValueError:
                pass

        notify_date = self.request.query_params.get('notify_date')
        if notify_date:
            parsed = parse_date(notify_date)
            if parsed:
                qs = qs.filter(notify_date=parsed)

        return qs

    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_id>[^/.]+)')
    def user_notifications(self, request, user_id=None):
        """Return notifications for a specific user.

        - Superusers may view any user's notifications.
        - Regular users may only view their own notifications.
        Supports the same query params as the list view (`is_read`, `notify_date`).
        """
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            return Response({'detail': 'Invalid user id'}, status=status.HTTP_400_BAD_REQUEST)

        if not (request.user.is_superuser or request.user.id == uid):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        qs = Notification.objects.filter(user__id=uid).order_by('-notify_date', '-created_at')

        # apply same filtering options
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() in ['true', '1']:
                qs = qs.filter(is_read=True)
            elif is_read.lower() in ['false', '0']:
                qs = qs.filter(is_read=False)

        notify_date = request.query_params.get('notify_date')
        if notify_date:
            parsed = parse_date(notify_date)
            if parsed:
                qs = qs.filter(notify_date=parsed)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='unread_count')
    def unread_count(self, request):
        """Return unread notification count.

        - Regular users get their unread count.
        - Superusers may pass `?user=<id>` to get any user's unread count.
        """
        target_user = request.user
        if request.user.is_superuser:
            user_param = request.query_params.get('user')
            if user_param:
                try:
                    uid = int(user_param)
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    target_user = User.objects.get(pk=uid)
                except Exception:
                    return Response({'detail': 'Invalid user id'}, status=status.HTTP_400_BAD_REQUEST)

        count = Notification.objects.filter(user=target_user, is_read=False).count()
        return Response({'unread_count': count})

    def perform_create(self, serializer):
        # If the request user is not a superuser, force the notification user to be the request.user
        if not self.request.user.is_superuser:
            serializer.save(user=self.request.user)
        else:
            # superuser may specify `user` in payload; if not provided, default to request.user
            if serializer.validated_data.get('user'):
                serializer.save()
            else:
                serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        qs = self.get_queryset().filter(is_read=False)
        qs.update(is_read=True)
        return Response({'marked': qs.count()}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        obj = self.get_object()
        obj.is_read = True
        obj.save()
        return Response({'id': obj.id, 'is_read': obj.is_read}, status=status.HTTP_200_OK)
