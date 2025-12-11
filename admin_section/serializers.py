# admin_section/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MonthlyTarget, Sale, SalaryConfig
from attendance.models import WorkType, HourlyReport, WorkDetail, WorkPlan, WorkPlanTitle, UserProfile, Project, DailySummaryReport

class ProjectSerializer_admin(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    remaining_plots = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'created_by',
            'created_by_name',
            'name',
            'project_type',
            'description',
            'total_plots',
            'available_plots',
            'sold_plots',
            'remaining_plots',
            'address',
            'city',
            'state',
            'pincode',
            'launch_date',
            'expected_completion_date',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at', 'updated_at', 'remaining_plots']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class MonthlyTargetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'user_id', 'month', 'year', 'target_area', 'carry_forward']

class SaleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Sale
        fields = ['id', 'user', 'user_id', 'month', 'year', 'area_sold']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'designation', 'department', 'mobile_number',
            'date_of_birth', 'gender', 'marital_status', 'aadhaar_number', 'pan_number',
            'locality', 'city', 'state', 'pincode'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_superuser', 'date_joined', 'profile']

class SalaryConfigSerializer(serializers.ModelSerializer):
    daily_salary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalaryConfig
        fields = [
            'id', 'user', 'monthly_salary', 'working_days',
            'late_allowed_time', 'early_leave_allowed_time',
            'target_area', 'target_penalty_amount',
            'daily_salary'
        ]
        read_only_fields = ['daily_salary']

    def get_daily_salary(self, obj):
        try:
            return round(float(obj.daily_salary()), 2)
        except Exception:
            return 0.0

class WorkPlanTitleSerializer_admin(serializers.ModelSerializer):
    class Meta:
        model = WorkPlanTitle
        fields = ['id', 'title', 'description']

class WorkPlanSerializer_admin(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = WorkPlan
        fields = [
            'id', 'created_by', 'created_by_name', 'coworkers', 'titles',
            'description', 'status', 'type', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'type', 'created_at']


class WorkTypeSerializer_admin(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = '__all__'



class HourlyReportSerializer_admin(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = HourlyReport
        fields = [
            'id', 'user', 'user_name', 'report_date', 'report_hour',
            'location_latitude', 'location_longitude', 'work_done',
            'reason_not_done', 'work_types', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class WorkDetailSerializer_admin(serializers.ModelSerializer):
    hourly_report_info = serializers.CharField(source='hourly_report.__str__', read_only=True)
    work_type_name = serializers.CharField(source='work_type.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = WorkDetail
        fields = [
            'id',
            'hourly_report', 'hourly_report_info',

            'work_type', 'work_type_name',
            'project', 'project_name',

            'customer_name',
            'mobile_number',
            'plot_number',

            'customer_response',
            'reason_not_interested',
            'other_reason',

            'site_visit_done',
            'meeting_done',
            'booking_done',

            'next_followup_date',

            'area',                      
            'rate',
            'total_value',
            'tcm',
            'value_per_sqft',

            'feedback',

            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DailySummarySerializer_admin(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DailySummaryReport
        fields = [
            'id', 'user', 'user_name',
            'report_date',
            'summary_text',
            'total_hours',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Prevent creating a summary if hourly reports exist for that user/date.
        Admin may still want to override — change this behaviour if required.
        """
        user = data.get('user')
        report_date = data.get('report_date')
        if user and report_date:
            if HourlyReport.objects.filter(user=user, report_date=report_date).exists():
                raise serializers.ValidationError(
                    "Hourly Reports already exist for this user and date. Create summary with caution or delete hourly reports first."
                )
        return 
    


# admin_section/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from attendance.models import Project
from .models import Incentive


class IncentiveSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Incentive
        fields = [
            'id',

            'user', 'user_name',
            'project', 'project_name',

            'plot_number',
            'mouza',

            'total_price',
            'commission_price',
            'advance_commission',
            'total_paid_commission',   # ✅ FIXED (added)
            'balance_commission',

            'deal_date',
            'customer_name',
            'customer_mobile',

            'remarks',

            'created_at',
            'updated_at',
        ]

        # Balance auto-calculated → read-only
        read_only_fields = [
            'id',
            'balance_commission',
            'created_at',
            'updated_at'
        ]
