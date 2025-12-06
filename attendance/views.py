# attendance/views.py
import random, string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import permissions
from django.db.models import Q
from calendar import monthrange
from datetime import date, timedelta
import calendar
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.decorators import action
from .serializers import SignupSerializer, VerifyOTPSerializer, LoginSerializer, UserProfileSerializer, UserTargetStatusSerializer, WorkPlanSerializer, WorkPlanCreateSerializer,HourlyReportSerializer, HourlyReportCreateSerializer, AttendanceSerializer, ProjectSerializer, WorkTypeSerializer, WorkPlanTitleSerializer, UserDropdownSerializer, WorkPlanTitleDropdownSerializer, DailySummarySerializer
from .models import WorkPlan, HourlyReport, Attendance, Project, WorkType, WorkPlanTitle, DailySummaryReport
from admin_section.models import SalaryConfig, Sale, MonthlyTarget
from django.utils.timezone import localtime

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
        if last_sent and (localtime(timezone.now()) - last_sent).total_seconds() < 60:
            return Response(
                {"error": "OTP already sent recently. Please wait before requesting again."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Generate new OTP
        otp = generate_otp()
        cached_data['otp'] = otp
        cache.set(cache_key, cached_data, timeout=600)  # OTP valid for 10 minutes
        cache.set(last_sent_key, localtime(timezone.now()), timeout=60)  # Rate limit

        # Send OTP via email
        send_mail(
            subject="Your OTP (Resent)",
            message=f"Your new OTP is {otp}. It will expire in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({
            "message": "OTP resent successfully.",
            "otp_last_sent": localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
            }, status=status.HTTP_200_OK)

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

class UserTargetStatusAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user != user and not request.user.is_staff:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        year_param = request.query_params.get('year', None)
        year = int(year_param) if year_param else date.today().year

        # Previous December carry
        previous_year = year - 1
        december_carry = 0

        try:
            prev_dec = MonthlyTarget.objects.get(user=user, year=previous_year, month=12)
            dec_sold = Sale.objects.filter(
                user=user, year=previous_year, month=12
            ).aggregate(total=Sum('area_sold'))["total"] or 0

            december_carry = max(0, dec_sold - prev_dec.target_area)

        except MonthlyTarget.DoesNotExist:
            december_carry = 0

        # Current year
        targets = MonthlyTarget.objects.filter(user=user, year=year).order_by("month")

        monthly_status = []
        running_carry = 0
        first_month = True

        for t in targets:
            sold = Sale.objects.filter(
                user=user, year=year, month=t.month
            ).aggregate(total=Sum('area_sold'))["total"] or 0

            # Carry logic
            if first_month:
                carry_from_last_month = december_carry
                effective = sold + december_carry
                first_month = False
            else:
                carry_from_last_month = running_carry
                effective = sold + running_carry

            if effective >= t.target_area:
                status_str = "green"
                new_carry = effective - t.target_area
            else:
                status_str = "red"
                new_carry = 0

            monthly_status.append({
                "month": t.get_month_display(),
                "target_area": float(t.target_area),
                "sold_area": float(sold),
                "status": status_str,
                "carry_from_last_month": float(carry_from_last_month),
                "carry_forward": float(new_carry),
            })

            running_carry = new_carry

        # ⛔ NO SERIALIZER — DIRECT JSON RETURN
        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "year": year,
            "monthly_status": monthly_status
        })

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

        attendance.check_in_time = localtime(timezone.now())
        attendance.check_in_latitude = latitude
        attendance.check_in_longitude = longitude
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response({
            "message": "Successfully checked in.",
            "check_in_time": attendance.check_in_time.strftime("%I:%M %p"),
            "attendance": AttendanceSerializer(attendance).data
        }, status=status.HTTP_200_OK)

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

        attendance.check_out_time = localtime(timezone.now())
        attendance.check_out_latitude = latitude
        attendance.check_out_longitude = longitude
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response({
            "message": "Successfully checked out.",
            "check_out_time": attendance.check_out_time.strftime("%I:%M %p"),
            "attendance": AttendanceSerializer(attendance).data
        }, status=status.HTTP_200_OK)

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


class WorkPlanDropdownsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        coworkers = User.objects.all()  # You can filter by department if needed
        titles = WorkPlanTitle.objects.all()
        
        coworker_data = UserDropdownSerializer(coworkers, many=True).data
        title_data = WorkPlanTitleDropdownSerializer(titles, many=True).data
        
        return Response({
            "coworkers": coworker_data,
            "titles": title_data
        })


class HourlyReportCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HourlyReportCreateSerializer

class DailySummaryCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DailySummarySerializer

    def get_queryset(self):
        return DailySummaryReport.objects.filter(user=self.request.user)


class DailySummaryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DailySummarySerializer

    def get_queryset(self):
        return DailySummaryReport.objects.filter(user=self.request.user).order_by('-report_date')


class DailySummaryUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DailySummarySerializer

    def get_queryset(self):
        return DailySummaryReport.objects.filter(user=self.request.user)


class HourlyReportListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HourlyReportSerializer

    def get_queryset(self):
        return HourlyReport.objects.filter(user=self.request.user).order_by('-report_date', '-report_hour')

class HourlyReportUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HourlyReportCreateSerializer  # You can use same serializer for update
    queryset = HourlyReport.objects.all()

    def get_queryset(self):
        # User can update only his own reports
        return HourlyReport.objects.filter(user=self.request.user)


class WorkTypeListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        work_types = WorkType.objects.all()
        serializer = WorkTypeSerializer(work_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkPlanTitleListAPIView(APIView):
    def get(self, request):
        titles = WorkPlanTitle.objects.all()
        serializer = WorkPlanTitleSerializer(titles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProjectListAPIView(APIView):
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserSalarySlipViewSet(viewsets.ViewSet):
    """
    Employee Salary Slip API (User Side)
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def slip(self, request):
        user = request.user
        today = date.today()

        # -----------------------
        # Month & Year Input
        # -----------------------
        try:
            month = int(request.query_params.get("month", today.month))
            year = int(request.query_params.get("year", today.year))
        except:
            return Response({"error": "Invalid month/year"}, status=400)

        total_days = calendar.monthrange(year, month)[1]

        # CONSTANTS
        ALLOWED_LEAVES = 4
        HALF = Decimal("0.5")
        ROUND_Q = Decimal("0.01")

        # -----------------------
        # SALARY CONFIG
        # -----------------------
        try:
            cfg = SalaryConfig.objects.get(user=user)
            monthly_salary = Decimal(str(cfg.monthly_salary))
            working_days = cfg.working_days

            daily_salary = (monthly_salary / Decimal(working_days)).quantize(
                ROUND_Q, rounding=ROUND_HALF_UP
            )
        except SalaryConfig.DoesNotExist:
            return Response({"error": "Salary configuration not found"}, status=404)

        # -----------------------
        # SALES TARGET
        # -----------------------
        target_obj = MonthlyTarget.objects.filter(
            user=user, month=month, year=year
        ).first()

        target_area = float(target_obj.target_area) if target_obj else 0.0

        sale_data = Sale.objects.filter(
            user=user, month=month, year=year
        ).aggregate(total=Sum("area_sold"))

        sales_sum = float(sale_data["total"]) if sale_data["total"] else 0.0

        # -----------------------
        # ATTENDANCE PROCESSING
        # -----------------------
        present_days = 0
        absent_days = 0
        half_day_counter = Decimal("0")
        attendance_days = []

        for day in range(1, total_days + 1):
            current_date = date(year, month, day)
            att = Attendance.objects.filter(user=user, date=current_date).first()

            # Future dates
            if current_date > today:
                attendance_days.append("-")
                continue

            # ABSENT
            if not att or not att.check_in_time:
                absent_days += 1
                attendance_days.append("A")
                continue

            # PRESENT
            present_days += 1
            attendance_days.append("P")

            is_late_half = False
            is_early_half = False

            # Late Check
            if att.check_in_time and att.check_in_time.time() > cfg.late_allowed_time:
                is_late_half = True

            # Early Leave Check
            if att.check_out_time and att.check_out_time.time() < cfg.early_leave_allowed_time:
                is_early_half = True

            # Apply half-day rules
            if is_late_half and is_early_half:
                half_day_counter += Decimal("1.0")  # FULL DAY
            elif is_late_half:
                half_day_counter += HALF
            elif is_early_half:
                half_day_counter += HALF

        # -----------------------
        # DEDUCTIONS
        # -----------------------
        unpaid_absences = max(0, absent_days - ALLOWED_LEAVES)

        half_day_deduction = (half_day_counter * (daily_salary / 1)).quantize(
            ROUND_Q, rounding=ROUND_HALF_UP
        )

        absence_deduction = (Decimal(unpaid_absences) * daily_salary).quantize(
            ROUND_Q, rounding=ROUND_HALF_UP
        )

        target_penalty = Decimal("0.00")
        if target_area > 0 and sales_sum < target_area:
            target_penalty = Decimal(str(cfg.target_penalty_amount))

        gross_salary = (Decimal(present_days) * daily_salary).quantize(
            ROUND_Q, rounding=ROUND_HALF_UP
        )

        total_deduction = (half_day_deduction + absence_deduction + target_penalty).quantize(
            ROUND_Q
        )

        net_salary = gross_salary - total_deduction
        if net_salary < 0:
            net_salary = Decimal("0.00")

        # -----------------------
        # RESPONSE
        # -----------------------
        slip = {
            "month": month,
            "year": year,

            "monthly_salary": float(monthly_salary),
            "working_days": working_days,
            "daily_salary": float(daily_salary),

            "present_days": present_days,
            "absent_days": absent_days,
            "allowed_leaves": ALLOWED_LEAVES,
            "unpaid_absences": unpaid_absences,

            "half_day_count": float(half_day_counter),
            "half_day_deduction": float(half_day_deduction),
            "absence_deduction": float(absence_deduction),

            "target_area": target_area,
            "sales_sum": sales_sum,
            "target_penalty": float(target_penalty),

            "gross_salary": float(gross_salary),
            "total_deduction": float(total_deduction),
            "net_salary": float(net_salary),

            "attendance_calendar": attendance_days
        }

        return Response(slip, status=200)



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import User
from .models import HourlyReport


class SimpleHourlyReportCheckAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        now = timezone.localtime()
        today = timezone.localdate()
        current_hour = now.hour

        # Time limit: 11 AM – 7 PM
        if not (11 <= current_hour <= 19):
            return Response({
                "message": "This API works only between 11 AM and 7 PM."
            })

        # If superuser → check all employee reports
        if request.user.is_superuser:
            missing = []

            for user in User.objects.filter(is_superuser=False):
                exists = HourlyReport.objects.filter(
                    user=user,
                    report_date=today,
                    report_hour=current_hour
                ).exists()

                if not exists:
                    missing.append(user.username)

            if missing:
                return Response({
                    "message": "Some users have not submitted their hourly report.",
                    "missing_users": missing
                })

            return Response({
                "message": "All users have submitted their hourly report."
            })

        # If normal user → check own report
        report_exists = HourlyReport.objects.filter(
            user=request.user,
            report_date=today,
            report_hour=current_hour
        ).exists()

        if report_exists:
            return Response({
                "message": "You have already submitted your hourly report."
            })

        return Response({
            "message": "You need to submit your hourly report."
        })
