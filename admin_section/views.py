# admin_section/views.py
from django.shortcuts import get_object_or_404
from .models import MonthlyTarget, Sale, SalaryConfig, ContactUs
from rest_framework import viewsets, permissions, status
from rest_framework.viewsets import ViewSet
from django.db import models
from rest_framework.response import Response
from django.db.models import Sum
from django.contrib.auth.models import User
from .permissions import IsSuperUser
from rest_framework.decorators import action
from attendance.models import WorkType, HourlyReport, WorkDetail, Attendance, UserProfile, WorkPlanTitle, WorkPlan, Project, DailySummaryReport
from rest_framework.permissions import IsAuthenticated
from datetime import date
import calendar
from geopy.geocoders import Nominatim
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from .serializers import (
    WorkTypeSerializer_admin,
    HourlyReportSerializer_admin, WorkDetailSerializer_admin,WorkPlanSerializer_admin,SalaryConfigSerializer, WorkPlanTitleSerializer_admin, MonthlyTargetSerializer, SaleSerializer, UserSerializer, UserProfileSerializer, ProjectSerializer_admin, DailySummarySerializer_admin, ContactUsSerializer
)

from .permissions import IsSuperUser

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer_admin
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MonthlyTargetViewSet(viewsets.ModelViewSet):
    queryset = MonthlyTarget.objects.all()
    serializer_class = MonthlyTargetSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def perform_create(self, serializer):
        serializer.save()

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def perform_create(self, serializer):
        serializer.save()

class UserTargetStatusViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def list(self, request):
        """Show target/sale summary for all users."""
        year = date.today().year
        users = User.objects.all().order_by('id')
        response_data = []

        for user in users:
            targets = MonthlyTarget.objects.filter(user=user, year=year).order_by('month')
            if not targets.exists():
                continue  

            monthly_status = []
            carry_forward = 0

            for target in targets:
                sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
                total_sold = sales['total_sold'] or 0
                effective_sold = total_sold + carry_forward

                if effective_sold >= target.target_area:
                    status_color = 'green'
                    carry_forward = effective_sold - target.target_area
                else:
                    status_color = 'red'
                    carry_forward = 0

                monthly_status.append({
                    'month': target.get_month_display(),
                    'target_area': target.target_area,
                    'sold_area': total_sold,
                    'status': status_color,
                    'carry_forward': carry_forward,
                })

            response_data.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'year': year,
                'monthly_status': monthly_status
            })

        return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Show target/sale summary for one user."""
        user = get_object_or_404(User, id=pk)
        year = date.today().year
        targets = MonthlyTarget.objects.filter(user=user, year=year).order_by('month')

        if not targets.exists():
            return Response({"detail": "No targets found for this user."}, status=status.HTTP_404_NOT_FOUND)

        monthly_status = []
        carry_forward = 0

        for target in targets:
            sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
            total_sold = sales['total_sold'] or 0
            effective_sold = total_sold + carry_forward

            if effective_sold >= target.target_area:
                status_color = 'green'
                carry_forward = effective_sold - target.target_area
            else:
                status_color = 'red'
                carry_forward = 0

            monthly_status.append({
                'month': target.get_month_display(),
                'target_area': target.target_area,
                'sold_area': total_sold,
                'status': status_color,
                'carry_forward': carry_forward,
            })

        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'year': year,
            'monthly_status': monthly_status
        }, status=status.HTTP_200_OK)

class TargetAndSaleDashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for showing target and sale dashboard summary.
    Only accessible by superusers.
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def list(self, request):
        today = date.today()

        year = int(request.query_params.get('year', today.year))
        month = request.query_params.get('month')
        if month:
            month = int(month)

        total_targets = MonthlyTarget.objects.filter(year=year)
        total_sales = Sale.objects.filter(year=year)
        total_users = User.objects.exclude(is_superuser=True).count()

        total_target_area = total_targets.aggregate(total=Sum('target_area'))['total'] or 0
        total_sold_area = total_sales.aggregate(total=Sum('area_sold'))['total'] or 0

        progress_percent = round((total_sold_area / total_target_area) * 100, 2) if total_target_area else 0.0

        users_status = []
        users = User.objects.exclude(is_superuser=True).order_by('username')

        for user in users:
            user_targets = MonthlyTarget.objects.filter(user=user, year=year)
            if month:
                user_targets = user_targets.filter(month=month)
            user_targets = user_targets.order_by('month')

            monthly_status = []
            carry_forward = 0

            for target in user_targets:
                sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
                total_sold = sales['total_sold'] or 0
                effective_sold = total_sold + carry_forward

                if effective_sold >= target.target_area:
                    status_color = 'green'
                    carry_forward = effective_sold - target.target_area
                else:
                    status_color = 'red'
                    carry_forward = 0

                monthly_status.append({
                    'month': target.get_month_display(),
                    'target_area': target.target_area,
                    'sold_area': total_sold,
                    'status': status_color,
                    'carry_forward': carry_forward,
                })

            users_status.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'monthly_status': monthly_status,
            })

        data = {
            'year': year,
            'month': month,
            'total_targets_count': total_targets.count(),
            'total_sales_count': total_sales.count(),
            'total_users_count': total_users,
            'total_target_area': total_target_area,
            'total_sold_area': total_sold_area,
            'progress_percent': progress_percent,
            'users_status': users_status,
        }

        return Response(data, status=status.HTTP_200_OK)

class AdminUserViewSet(viewsets.ViewSet):
    permission_classes = [IsSuperUser]

    def list(self, request):
        filter_type = request.query_params.get('filter', 'all')

        users = User.objects.all().order_by('-date_joined')
        if filter_type == 'pending':
            users = users.filter(is_active=False, is_superuser=False)
        elif filter_type == 'approved':
            users = users.filter(is_active=True, is_superuser=False)
        elif filter_type == 'admins':
            users = users.filter(is_superuser=True)

        serializer = UserSerializer(users, many=True)
        return Response({
            "summary": {
                "total_users": User.objects.exclude(is_superuser=True).count(),
                "approved_users": User.objects.filter(is_active=True, is_superuser=False).count(),
                "pending_users": User.objects.filter(is_active=False, is_superuser=False).count(),
                "super_users": User.objects.filter(is_superuser=True).count(),
                "active_filter": filter_type,
            },
            "users": serializer.data
        })

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save()
        return Response({"message": f"{user.username} approved successfully."})

    @action(detail=True, methods=['put'])
    def edit(self, request, pk=None):
        """
        ✅ Update user info + profile safely.
        """
        user = get_object_or_404(User, pk=pk)

        user.username = request.data.get('username', user.username)
        user.email = request.data.get('email', user.email)
        user.save()

        profile_data = request.data.get('profile', {})
        profile, created = UserProfile.objects.get_or_create(user=user)

        serializer = UserProfileSerializer(profile, data=profile_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = UserSerializer(user)
        return Response({
            "message": "User and profile updated successfully.",
            "user": user_serializer.data
        })

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

HALF = Decimal("0.5")
ROUND_Q = Decimal("0.01")

# ------------------------------------------------------
# SalaryConfig CRUD
# ------------------------------------------------------

class SalaryConfigViewSet(viewsets.ModelViewSet):
    queryset = SalaryConfig.objects.all().order_by("user__username")
    serializer_class = SalaryConfigSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'list']:
            return [IsSuperUser()]
        return super().get_permissions()

# ------------------------------------------------------
# Attendance + Salary Calculations
# ------------------------------------------------------


ROUND_Q = Decimal("0.01")
HALF = Decimal("0.5")
ALLOWED_LEAVES = 4


class AttendanceDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSuperUser]

    # --------------------------------------------------
    # DAILY STATUS (OK – minor optimization only)
    # --------------------------------------------------

    @action(detail=False, methods=["get"])
    def daily(self, request):
        today = date.today()
        users = User.objects.exclude(is_superuser=True).order_by("username")

        geolocator = Nominatim(user_agent="attendance_app")

        present_count = 0
        absent_count = 0
        data = []

        def get_location(lat, lon):
            if lat and lon:
                try:
                    loc = geolocator.reverse(f"{lat},{lon}", timeout=10)
                    return loc.address if loc else "-"
                except:
                    return "-"
            return "-"

        for user in users:
            att = Attendance.objects.filter(user=user, date=today).first()

            if att and att.check_in_time:
                status = "Present"
                present_count += 1
            else:
                status = "Absent"
                absent_count += 1

            data.append({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "status": status,
                "check_in": timezone.localtime(att.check_in_time).strftime("%H:%M:%S") if att and att.check_in_time else "-",
                "check_in_location": get_location(att.check_in_latitude, att.check_in_longitude) if att else "-",
                "check_out": timezone.localtime(att.check_out_time).strftime("%H:%M:%S") if att and att.check_out_time else "-",
                "check_out_location": get_location(att.check_out_latitude, att.check_out_longitude) if att else "-"
            })

        return Response({
            "date": str(today),
            "total_employees": users.count(),
            "present": present_count,
            "absent": absent_count,
            "attendance": data
        })

    # --------------------------------------------------
    # MONTHLY SALARY (FIXED & CONSISTENT)
    # --------------------------------------------------

    @action(detail=False, methods=["get"])
    def monthly(self, request):
        today = date.today()
        month = int(request.query_params.get("month", today.month))
        year = int(request.query_params.get("year", today.year))
        total_days = calendar.monthrange(year, month)[1]

        users = User.objects.exclude(is_superuser=True).order_by("username")
        report = []

        for user in users:
            try:
                cfg = user.salary_config
            except:
                report.append({"user": user.username, "error": "SalaryConfig missing"})
                continue

            monthly_salary = Decimal(str(cfg.monthly_salary))
            working_days = cfg.working_days
            daily_salary = (monthly_salary / Decimal(working_days)).quantize(
                ROUND_Q, rounding=ROUND_HALF_UP
            )

            # Target & Sales
            mt = MonthlyTarget.objects.filter(user=user, month=month, year=year).first()
            target_area = float(mt.target_area) if mt else None

            sales = Sale.objects.filter(user=user, month=month, year=year).aggregate(sum=Sum("area_sold"))
            sales_total = float(sales["sum"]) if sales["sum"] else 0

            present_days = 0
            absent_days = 0
            half_day_count = Decimal("0")
            daily_details = []

            for day in range(1, total_days + 1):
                d = date(year, month, day)
                att = Attendance.objects.filter(user=user, date=d).first()

                if d > today:
                    daily_details.append({"date": str(d), "status": "-"})
                    continue

                if not att or not att.check_in_time:
                    absent_days += 1
                    daily_details.append({
                        "date": str(d),
                        "status": "Absent",
                        "deduction": 0
                    })
                    continue

                present_days += 1

                late = att.check_in_time.time() > cfg.late_allowed_time
                early = att.check_out_time and att.check_out_time.time() < cfg.early_leave_allowed_time

                if late and early:
                    half = Decimal("1.0")
                elif late or early:
                    half = HALF
                else:
                    half = Decimal("0")

                half_day_count += half

                daily_details.append({
                    "date": str(d),
                    "status": "Present" if half == 0 else "Half Day" if half == HALF else "Full Deduct",
                    "half_day": float(half),
                    "late": late,
                    "early_leave": early
                })

            # -----------------------
            # DEDUCTIONS (CORRECT)
            # -----------------------

            if present_days == 0:
                unpaid_absences = working_days
            else:
                unpaid_absences = max(0, absent_days - ALLOWED_LEAVES)

            absence_deduction = (Decimal(unpaid_absences) * daily_salary).quantize(ROUND_Q)
            half_day_deduction = (half_day_count * daily_salary).quantize(ROUND_Q)

            target_penalty = Decimal("0.00")
            if target_area is not None and sales_total < target_area:
                target_penalty = Decimal(str(cfg.target_penalty_amount))

            total_deduction = (
                absence_deduction +
                half_day_deduction +
                target_penalty
            ).quantize(ROUND_Q)

            net_salary = monthly_salary - total_deduction
            if net_salary < 0:
                net_salary = Decimal("0.00")

            report.append({
                "user_id": user.id,
                "username": user.username,

                "monthly_salary": float(monthly_salary),
                "daily_salary": float(daily_salary),

                "present_days": present_days,
                "absent_days": absent_days,
                "allowed_leaves": ALLOWED_LEAVES,
                "unpaid_absences": unpaid_absences,

                "half_day_count": float(half_day_count),
                "absence_deduction": float(absence_deduction),
                "half_day_deduction": float(half_day_deduction),
                "target_penalty": float(target_penalty),

                "total_deduction": float(total_deduction),
                "net_salary": float(net_salary),

                "sales_total": sales_total,
                "target_area": target_area,

                "daily_details": daily_details
            })

        return Response({
            "month": month,
            "year": year,
            "report": report
        })

class WorkPlanTitleViewSet(viewsets.ModelViewSet):
    """
    Superuser-only CRUD for WorkPlan Titles
    """
    queryset = WorkPlanTitle.objects.all().order_by('title')
    serializer_class = WorkPlanTitleSerializer_admin
    permission_classes = [IsAuthenticated, IsSuperUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "WorkPlan Title created successfully!", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "WorkPlan Title updated successfully!", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "WorkPlan Title deleted successfully!"}, status=status.HTTP_200_OK)

class AdminWorkPlanViewSet(viewsets.ModelViewSet):
    """
    API for Superusers to manage Admin-Created WorkPlans
    """
    serializer_class = WorkPlanSerializer_admin
    permission_classes = [IsAuthenticated, IsSuperUser]

    def get_queryset(self):
        return WorkPlan.objects.filter(type='admin_created').order_by('-date')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, type='admin_created')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "✅ Admin work plan created successfully!", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Work plan updated successfully!", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Work plan deleted successfully!"}, status=status.HTTP_200_OK)

class UserWorkPlanViewSet(viewsets.ModelViewSet):
    serializer_class = WorkPlanSerializer_admin
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Superuser should see all user-created workplans
        if user.is_superuser:
            return WorkPlan.objects.filter(type='user_created').order_by('-date')

        # Normal users see only their own
        return WorkPlan.objects.filter(
            created_by=user,
            type='user_created'
        ).order_by('-date')

    def perform_create(self, serializer):
        """Automatically assign created_by and type."""
        serializer.save(created_by=self.request.user, type='user_created')

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """Get all workplans for a specific month and year."""
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not month or not year:
            return Response({'error': 'Please provide month and year in query parameters.'}, status=status.HTTP_400_BAD_REQUEST)

        workplans = WorkPlan.objects.filter(
            created_by=request.user,
            type='user_created',
            date__year=year,
            date__month=month
        ).order_by('-date')

        serializer = self.get_serializer(workplans, many=True)
        return Response(serializer.data)

class WorkTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkType.objects.all()
    serializer_class = WorkTypeSerializer_admin
    permission_classes = [permissions.IsAuthenticated]

class HourlyReportViewSet(viewsets.ModelViewSet):
    serializer_class = HourlyReportSerializer_admin
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HourlyReport.objects.filter(user=self.request.user).order_by('-report_date', '-report_hour')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkDetailViewSet(viewsets.ModelViewSet):
    serializer_class = WorkDetailSerializer_admin
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkDetail.objects.select_related(
            'hourly_report',
            'work_type',
            'project'
        )


def calculate_total_hours(user, report_date):
    """
    Currently counts number of hourly reports for that date.
    Change logic if you want sum over an 'hours' field.
    """
    return HourlyReport.objects.filter(user=user, report_date=report_date).count()


class DailySummaryViewSet_admin(viewsets.ModelViewSet):
    serializer_class = DailySummarySerializer_admin
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = DailySummaryReport.objects.select_related('user').all().order_by('-report_date')
        user_id = self.request.query_params.get('user_id')
        date = self.request.query_params.get('date')

        if user_id:
            qs = qs.filter(user__id=user_id)
        if date:
            qs = qs.filter(report_date=date)

        return qs

    def perform_create(self, serializer):
        """
        Optionally auto-calculate total_hours based on existing hourly reports.
        Admin can still override total_hours by including it in payload.
        """
        user = serializer.validated_data.get('user', None)
        report_date = serializer.validated_data.get('report_date', None)

        # If admin didn't pass total_hours explicitly, calculate it
        if serializer.validated_data.get('total_hours') in (None, '') and user and report_date:
            total_hours = calculate_total_hours(user, report_date)
            serializer.save(total_hours=total_hours)
        else:
            serializer.save()

class DashboardViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def list(self, request):
        today = date.today()

        # ----------------------
        # USER & ATTENDANCE DATA
        # ----------------------

        users = User.objects.exclude(is_superuser=True)
        total_users = users.count()

        checked_in_att = Attendance.objects.filter(date=today, check_in_time__isnull=False)
        checked_out_att = Attendance.objects.filter(date=today, check_out_time__isnull=False)

        checked_in_count = checked_in_att.count()
        not_checked_in_count = total_users - checked_in_count

        # Helper to get full name
        def get_user_name(user):
            try:
                full = f"{user.profile.first_name} {user.profile.last_name}".strip()
                return full or user.username
            except:
                return user.username

        # ----------------------
        # RECENT ACTIVITY
        # ----------------------

        recent_activity = []

        for u in users.filter(date_joined__date=today):
            recent_activity.append({
                "title": "User Signed Up",
                "description": f"{get_user_name(u)} signed up",
                "time": timezone.localtime(u.date_joined).strftime('%H:%M'),
                "user_id": u.id,
                "icon": "fa-user-plus",
                "color": "var(--info)"
            })

        for u in users.filter(last_login__date=today):
            recent_activity.append({
                "title": "User Logged In",
                "description": f"{get_user_name(u)} logged in",
                "time": timezone.localtime(u.last_login).strftime('%H:%M'),
                "user_id": u.id,
                "icon": "fa-sign-in-alt",
                "color": "var(--success)"
            })

        for att in checked_in_att:
            recent_activity.append({
                "title": "Checked In",
                "description": f"{get_user_name(att.user)} checked in at {timezone.localtime(att.check_in_time).strftime('%I:%M %p')}",
                "time": timezone.localtime(att.check_in_time).strftime('%H:%M'),
                "user_id": att.user.id,
                "icon": "fa-sign-in-alt",
                "color": "var(--success)"
            })

        for att in checked_out_att:
            recent_activity.append({
                "title": "Checked Out / Logged Out",
                "description": f"{get_user_name(att.user)} checked out at {timezone.localtime(att.check_out_time).strftime('%I:%M %p')}",
                "time": timezone.localtime(att.check_out_time).strftime('%H:%M'),
                "user_id": att.user.id,
                "icon": "fa-sign-out-alt",
                "color": "var(--warning)"
            })

        for p in UserProfile.objects.filter(created_at__date=today):
            recent_activity.append({
                "title": "Profile Created",
                "description": f"{get_user_name(p.user)} created profile",
                "time": timezone.localtime(p.created_at).strftime('%H:%M'),
                "user_id": p.user.id,
                "icon": "fa-id-card",
                "color": "var(--info)"
            })

        for p in UserProfile.objects.filter(updated_at__date=today):
            recent_activity.append({
                "title": "Profile Updated",
                "description": f"{get_user_name(p.user)} updated profile",
                "time": timezone.localtime(p.updated_at).strftime('%H:%M'),
                "user_id": p.user.id,
                "icon": "fa-edit",
                "color": "var(--warning)"
            })

        for proj in Project.objects.filter(created_at__date=today):
            recent_activity.append({
                "title": "Project Created",
                "description": f"{proj.name} project created",
                "time": timezone.localtime(proj.created_at).strftime('%H:%M'),
                "user_id": proj.created_by.id if proj.created_by else None,
                "icon": "fa-building",
                "color": "var(--dark)"
            })

        for mt in MonthlyTarget.objects.filter(user__in=users, month=today.month, year=today.year):
            recent_activity.append({
                "title": "Monthly Target Set",
                "description": f"{get_user_name(mt.user)} set monthly target",
                "time": "09:00",
                "user_id": mt.user.id,
                "icon": "fa-bullseye",
                "color": "var(--primary)"
            })

        for sale in Sale.objects.filter(user__in=users, month=today.month, year=today.year):
            recent_activity.append({
                "title": "Sale Added",
                "description": f"{get_user_name(sale.user)} added sale {sale.area_sold} sq ft",
                "time": "09:30",
                "user_id": sale.user.id,
                "icon": "fa-chart-line",
                "color": "var(--success)"
            })

        for wp in WorkPlan.objects.filter(created_at__date=today):
            recent_activity.append({
                "title": "Work Plan Created",
                "description": f"{get_user_name(wp.created_by)} created a work plan",
                "time": timezone.localtime(wp.created_at).strftime('%H:%M'),
                "user_id": wp.created_by.id,
                "icon": "fa-tasks",
                "color": "var(--primary)"
            })

        for hr in HourlyReport.objects.filter(created_at__date=today):
            recent_activity.append({
                "title": "Hourly Report",
                "description": f"{get_user_name(hr.user)} submitted hourly report ({hr.report_hour}:00)",
                "time": timezone.localtime(hr.created_at).strftime('%H:%M'),
                "user_id": hr.user.id,
                "icon": "fa-clock",
                "color": "var(--info)"
            })

        recent_activity = sorted(recent_activity, key=lambda x: x['time'], reverse=True)

        # ----------------------
        # WORKPLAN SUMMARY
        # ----------------------

        workplans_today = WorkPlan.objects.filter(date=today)
        total_workplans = workplans_today.count()
        completed_workplans = workplans_today.filter(status='completed').count()
        pending_workplans = total_workplans - completed_workplans

        admin_workplans_count = WorkPlan.objects.filter(type='admin_created').count()
        user_workplans_count = WorkPlan.objects.filter(type='user_created').count()

        # ----------------------
        # WORKTYPE & OPTION DATA
        # ----------------------

        worktype_count = WorkType.objects.count()

        # ----------------------
        # HOURLY REPORT DATA
        # ----------------------

        hourly_total = HourlyReport.objects.count()
        hourly_today = HourlyReport.objects.filter(report_date=today).count()
        hourly_work_done = HourlyReport.objects.filter(work_done="yes").count()
        hourly_work_not_done = HourlyReport.objects.filter(work_done="no").count()

        # ----------------------
        # WORK DETAIL DATA
        # ----------------------

        workdetail_total = WorkDetail.objects.count()
        customer_response = {
            "interested": WorkDetail.objects.filter(customer_response='interested').count(),
            "not_interested": WorkDetail.objects.filter(customer_response='not_interested').count(),
            "not_sure": WorkDetail.objects.filter(customer_response='not_sure').count(),
        }
        project_details = (
            WorkDetail.objects.values('project__name')
            .order_by('project__name')
            .annotate(total=models.Count('id'))
        )

        # ----------------------
        # FINAL RESPONSE
        # ----------------------

        return Response({
            "total_users": total_users,
            "checked_in_count": checked_in_count,
            "not_checked_in_count": not_checked_in_count,
            "recent_activity": recent_activity,

            "total_workplans": total_workplans,
            "completed_workplans": completed_workplans,
            "pending_workplans": pending_workplans,
            "admin_workplans_count": admin_workplans_count,
            "user_workplans_count": user_workplans_count,

            "worktype_count": worktype_count,

            "hourly_report_total": hourly_total,
            "hourly_report_today": hourly_today,
            "hourly_work_done": hourly_work_done,
            "hourly_work_not_done": hourly_work_not_done,

            "workdetail_total": workdetail_total,
            "customer_response": customer_response,
            "project_wise_work_details": list(project_details),
        })


# admin_section/views.py

from rest_framework import viewsets, permissions
from .models import Incentive
from .serializers import IncentiveSerializer


class IncentiveViewSet(viewsets.ModelViewSet):
    queryset = Incentive.objects.select_related('user', 'project').all()
    serializer_class = IncentiveSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContactUsViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Contact Us form submissions
    - Anyone can create a contact form (POST without auth)
    - Only admin/superuser can view, update, delete, and reply
    """
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Allow unauthenticated users to create contact forms
        Require authentication and superuser for other actions
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsSuperUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Admin can see all contact forms
        Regular users can only see their own submissions
        """
        user = self.request.user
        if user.is_superuser:
            return ContactUs.objects.all()
        # Regular users can view their own submissions by email
        return ContactUs.objects.filter(email=user.email)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsSuperUser])
    def reply(self, request, pk=None):
        """
        Admin endpoint to reply to a contact form
        POST /api/contact-us/{id}/reply/
        
        Request body:
        {
            "admin_reply": "Thank you for your message..."
        }
        """
        contact = self.get_object()
        admin_reply = request.data.get('admin_reply')
        
        if not admin_reply:
            return Response(
                {"error": "admin_reply field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contact.admin_reply = admin_reply
        contact.status = 'replied'
        contact.replied_by = request.user
        contact.replied_at = timezone.now()
        contact.save()
        
        serializer = self.get_serializer(contact)
        return Response({
            "message": "Reply sent successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsSuperUser])
    def mark_as_read(self, request, pk=None):
        """
        Mark a contact form as read
        POST /api/contact-us/{id}/mark_as_read/
        """
        contact = self.get_object()
        contact.status = 'read'
        contact.save()
        
        serializer = self.get_serializer(contact)
        return Response({
            "message": "Marked as read",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsSuperUser])
    def close(self, request, pk=None):
        """
        Close a contact form
        POST /api/contact-us/{id}/close/
        """
        contact = self.get_object()
        contact.status = 'closed'
        contact.save()
        
        serializer = self.get_serializer(contact)
        return Response({
            "message": "Contact form closed",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
