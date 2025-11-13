from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MonthlyTarget, Sale

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


# admin_section/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from attendance.models import UserProfile

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


# admin_section/serializers.py
from rest_framework import serializers
from attendance.models import WorkPlanTitle

class WorkPlanTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPlanTitle
        fields = ['id', 'title', 'description']



# admin_section/serializers.py
from rest_framework import serializers
from attendance.models import WorkPlan

class WorkPlanSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = WorkPlan
        fields = [
            'id', 'created_by', 'created_by_name', 'coworkers', 'titles',
            'description', 'status', 'type', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'type', 'created_at']


from rest_framework import serializers
from attendance.models import WorkType, WorkTypeOption, HourlyReport, WorkDetail
from django.contrib.auth.models import User


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = '__all__'


class WorkTypeOptionSerializer(serializers.ModelSerializer):
    work_type_name = serializers.CharField(source='work_type.name', read_only=True)

    class Meta:
        model = WorkTypeOption
        fields = ['id', 'work_type', 'work_type_name', 'name', 'description']


class HourlyReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = HourlyReport
        fields = [
            'id', 'user', 'user_name', 'report_date', 'report_hour',
            'location_latitude', 'location_longitude', 'work_done', 'reason_not_done',
            'work_types', 'work_type_options', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class WorkDetailSerializer(serializers.ModelSerializer):
    hourly_report_info = serializers.CharField(source='hourly_report.__str__', read_only=True)
    work_type_option_name = serializers.CharField(source='work_type_option.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = WorkDetail
        fields = [
            'id', 'hourly_report', 'hourly_report_info', 'work_type_option',
            'work_type_option_name', 'project', 'project_name', 'customer_name',
            'mobile_number', 'plot_number', 'customer_response', 'reason_not_interested',
            'site_visit_done', 'meeting_done', 'booking_done', 'next_followup_date'
        ]
