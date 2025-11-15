# views.py
import random, string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, VerifyOTPSerializer, LoginSerializer
import os


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            otp = generate_otp()

            # Store in cache for 10 minutes
            cache_key = f"otp_{email}"
            cache.set(cache_key, {'email': email, 'password': password, 'otp': otp}, timeout=600)

            # Send OTP via email
            send_mail(
                subject='Your Email Verification OTP',
                message=f'Your OTP for the SHREE TAJ REALTOR is {otp}. It will expire in 10 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            return Response(
                {"message": "OTP sent to your email. Please verify to complete registration."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            cache_key = f"otp_{email}"
            cached_data = cache.get(cache_key)

            if not cached_data:
                return Response({"error": "OTP expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

            if cached_data['otp'] != otp:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

            # Create user now (after OTP success)
            user = User.objects.create_user(
                username=email,
                email=email,
                password=cached_data['password'],
                is_active=False  # Wait for admin approval
            )

            # Clear cache
            cache.delete(cache_key)

            return Response({
                "message": "Email verified successfully. Wait for admin approval.",
                "user_id": user.id
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful.",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "message": "Logout successful."
            }, status=status.HTTP_205_RESET_CONTENT)

        except TokenError:
            return Response({
                "error": "Invalid refresh token."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import random

def generate_otp():
    """Generate 6-digit numeric OTP"""
    return ''.join(random.choices('0123456789', k=6))


class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if there is an OTP already stored
        cache_key = f"otp_{email}"
        cached_data = cache.get(cache_key)

        if not cached_data:
            return Response(
                {"error": "No signup request found for this email or OTP expired. Please signup again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Rate limiting: allow resend only if last OTP was sent > 60 seconds ago
        last_sent_key = f"otp_last_sent_{email}"
        last_sent = cache.get(last_sent_key)
        if last_sent and (timezone.now() - last_sent).total_seconds() < 60:
            return Response(
                {"error": "OTP already sent recently. Please wait before requesting again."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Generate new OTP
        otp = generate_otp()
        cached_data['otp'] = otp
        cache.set(cache_key, cached_data, timeout=600)  # OTP valid for 10 minutes
        cache.set(last_sent_key, timezone.now(), timeout=60)  # Rate limit

        # Send OTP via email
        send_mail(
            subject="Your OTP (Resent)",
            message=f"Your new OTP is {otp}. It will expire in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"message": "OTP resent successfully."}, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializers import UserProfileSerializer

class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch profile
        if not hasattr(request.user, 'profile'):
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Check if profile already exists
        if hasattr(request.user, 'profile'):
            return Response({"error": "Profile already completed."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Profile completed successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Update profile
        if not hasattr(request.user, 'profile'):
            return Response({"error": "Profile not found. Complete profile first."}, status=status.HTTP_404_NOT_FOUND)

        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import date
from admin_section.models import MonthlyTarget, Sale
from .serializers import UserTargetStatusSerializer

class UserTargetStatusAPI(APIView):
    # Add JWT Authentication and permission
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, year=None):
        user = get_object_or_404(User, id=user_id)

        # Optional: restrict to the user himself or admin
        if request.user != user and not request.user.is_staff:
            return Response({"error": "You are not allowed to view this user's target."},
                            status=status.HTTP_403_FORBIDDEN)

        if not year:
            year = date.today().year  # default to current year

        targets = MonthlyTarget.objects.filter(user=user, year=year).order_by('month')
        monthly_status = []
        carry_forward = 0

        for target in targets:
            sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
            total_sold = sales['total_sold'] or 0

            effective_sold = total_sold + carry_forward

            if effective_sold >= target.target_area:
                status_str = 'green'
                carry_forward = effective_sold - target.target_area
            else:
                status_str = 'red'
                carry_forward = 0

            monthly_status.append({
                'month': target.get_month_display(),
                'target_area': target.target_area,
                'sold_area': total_sold,
                'status': status_str,
                'carry_forward': carry_forward
            })

        data = {
            'user_id': user.id,
            'user_email': user.email,
            'year': year,
            'monthly_status': monthly_status
        }

        serializer = UserTargetStatusSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer

# ----------------- CHECK-IN -----------------
class AttendanceCheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        # Get or create today's attendance
        attendance, created = Attendance.objects.get_or_create(user=user, date=timezone.localdate())

        if attendance.check_in_time:
            return Response(
                {"message": "You have already checked in today.", "attendance": AttendanceSerializer(attendance).data},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.check_in_time = timezone.now()
        attendance.check_in_latitude = latitude
        attendance.check_in_longitude = longitude
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(
            {"message": "Successfully checked in.", "attendance": serializer.data},
            status=status.HTTP_200_OK
        )


# ----------------- CHECK-OUT -----------------
class AttendanceCheckOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        try:
            attendance = Attendance.objects.get(user=user, date=timezone.localdate())
        except Attendance.DoesNotExist:
            return Response(
                {"message": "No check-in record found for today."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if attendance.check_out_time:
            return Response(
                {"message": "You have already checked out today.", "attendance": AttendanceSerializer(attendance).data},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.check_out_time = timezone.now()
        attendance.check_out_latitude = latitude
        attendance.check_out_longitude = longitude
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(
            {"message": "Successfully checked out.", "attendance": serializer.data},
            status=status.HTTP_200_OK
        )


from datetime import date
from calendar import monthrange
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class MonthlyAttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Current date details
        today = timezone.localdate()
        month = today.month
        year = today.year

        # Total days in current month (auto)
        total_days_in_month = monthrange(year, month)[1]

        # Get user's attendance for current month
        attendances = Attendance.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        )

        total_present_days = attendances.count()
        total_absent_days = total_days_in_month - total_present_days

        # Get today's attendance for last check-in/out
        last_check_in_time = None
        last_check_out_time = None
        last_date = None

        try:
            today_record = Attendance.objects.get(user=user, date=today)
            last_check_in_time = today_record.check_in_time
            last_check_out_time = today_record.check_out_time
            last_date = today_record.date
        except Attendance.DoesNotExist:
            pass

        return Response({
            "month": month,
            "year": year,
            "last_date": last_date,
            "last_check_in_time": last_check_in_time,
            "last_check_out_time": last_check_out_time,
            "total_days_in_month": total_days_in_month,
            "total_present_days": total_present_days,
            "total_absent_days": total_absent_days
        }, status=200)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

class TargetSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Calculate total target (sum of target_area + carry_forward)
        target_data = MonthlyTarget.objects.filter(user=user).aggregate(
            total_target=Sum('target_area') + Sum('carry_forward')
        )
        total_target = target_data['total_target'] if target_data['total_target'] else 0

        # Calculate total sale (sum of area_sold)
        sale_data = Sale.objects.filter(user=user).aggregate(total_sale=Sum('area_sold'))
        total_sale = sale_data['total_sale'] if sale_data['total_sale'] else 0

        # Remaining
        remaining_target = total_target - total_sale

        return Response({
            "total_target": total_target,
            "total_sale": total_sale,
            "remaining_target": remaining_target
        }, status=200)




from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from .models import WorkPlan
from .serializers import WorkPlanSerializer, WorkPlanCreateSerializer


class UserWorkPlanListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = WorkPlan.objects.filter(type='user_created').filter(
            Q(created_by=user) | Q(coworkers=user)
        )

        # Filter options
        filter_type = self.request.query_params.get('filter')  # daily, weekly, monthly
        today = timezone.localdate()

        if filter_type == 'daily':
            queryset = queryset.filter(date=today)
        elif filter_type == 'weekly':
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            queryset = queryset.filter(date__range=[start_of_week, end_of_week])
        elif filter_type == 'monthly':
            queryset = queryset.filter(date__year=today.year, date__month=today.month)

        # Title search
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(titles__title__icontains=title)

        # Manual date filter (optional)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset.order_by('-date')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkPlanCreateSerializer
        return WorkPlanSerializer

    def perform_create(self, serializer):
        serializer.save()


class UserWorkPlanDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkPlanSerializer
    queryset = WorkPlan.objects.filter(type='user_created')

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        status_value = request.data.get('status')
        if status_value:
            instance.status = status_value
            instance.save()
            return Response({
                "id": instance.id,
                "status": instance.status,
                "message": "Work plan status updated successfully!"
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from datetime import timedelta
from .models import WorkPlan
from .serializers import WorkPlanSerializer
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from datetime import timedelta
from collections import defaultdict
from django.utils import timezone
from .models import WorkPlan
from .serializers import WorkPlanSerializer


class UserWorkPlanAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()
        filter_type = request.query_params.get("filter")  # daily, weekly, monthly

        # Fetch both user-created and admin-created plans
        queryset = WorkPlan.objects.filter(
            Q(created_by=user) | Q(coworkers=user) | Q(type='admin_created')
        ).order_by('date')

        # Apply date-based filter
        if filter_type == 'daily':
            queryset = queryset.filter(date=today)

        elif filter_type == 'weekly':
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            queryset = queryset.filter(date__range=[start_of_week, end_of_week])

        elif filter_type == 'monthly':
            queryset = queryset.filter(date__year=today.year, date__month=today.month)

        # Group results by workplan type (user/admin)
        grouped_data = {
            "user_created": [],
            "admin_created": []
        }

        for wp in queryset:
            wp_data = WorkPlanSerializer(wp).data
            if wp.type == 'admin_created':
                grouped_data["admin_created"].append(wp_data)
            else:
                grouped_data["user_created"].append(wp_data)

        return Response({
            "filter_type": filter_type or "all",
            "total_count": queryset.count(),
            "data": grouped_data
        })


    

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import HourlyReport
from .serializers import HourlyReportSerializer, HourlyReportCreateSerializer

class HourlyReportCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HourlyReportCreateSerializer

class HourlyReportListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HourlyReportSerializer

    def get_queryset(self):
        return HourlyReport.objects.filter(user=self.request.user).order_by('-report_date', '-report_hour')

# Pending check API
class PendingHourlyReportCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.localtime()
        current_hour = now.hour
        today = now.date()

        exists = HourlyReport.objects.filter(
            user=user,
            report_date=today,
            report_hour=current_hour
        ).exists()

        if not exists:
            return Response({"pending": True, "message": f"Your hourly report for {current_hour}:00 is pending!"})
        return Response({"pending": False, "message": "All reports submitted for this hour."})


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WorkType
from .serializers import WorkTypeSerializer

class WorkTypeListAPIView(APIView):
    def get(self, request):
        work_types = WorkType.objects.prefetch_related('options').all()
        serializer = WorkTypeSerializer(work_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WorkPlanTitle
from .serializers import WorkPlanTitleSerializer

class WorkPlanTitleListAPIView(APIView):
    def get(self, request):
        titles = WorkPlanTitle.objects.all()
        serializer = WorkPlanTitleSerializer(titles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from .serializers import ProjectSerializer

class ProjectListAPIView(APIView):
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
