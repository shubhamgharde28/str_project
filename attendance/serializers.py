# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import HourlyReport, WorkDetail, WorkType, Attendance, WorkPlanTitle, UserProfile, WorkPlan, Project

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(username=data['email']).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return data

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Check if user exists
        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        # Check if user is active (admin approved)
        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is waiting for admin approval. Please contact support or try later."
            )

        data['user'] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ('user',)

class MonthlyStatusSerializer(serializers.Serializer):
    month = serializers.CharField()
    target_area = serializers.FloatField()
    sold_area = serializers.FloatField()
    status = serializers.CharField()
    carry_forward = serializers.FloatField()

class UserTargetStatusSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    year = serializers.IntegerField()
    monthly_status = MonthlyStatusSerializer(many=True)

class AttendanceSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'user', 'first_name', 'last_name', 'designation', 'department',
            'date', 'check_in_time', 'check_in_latitude', 'check_in_longitude',
            'check_out_time', 'check_out_latitude', 'check_out_longitude'
        ]
        read_only_fields = ['user', 'date', 'check_in_time', 'check_out_time']

    def get_first_name(self, obj):
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.first_name
        return None

    def get_last_name(self, obj):
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.last_name
        return None

    def get_designation(self, obj):
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.designation
        return None

    def get_department(self, obj):
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.department
        return None

class TargetSummarySerializer(serializers.Serializer):
    total_target = serializers.FloatField()
    total_sale = serializers.FloatField()
    remaining_target = serializers.FloatField()

class WorkPlanTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPlanTitle
        fields = ['id', 'title', 'description']


class UserDropdownSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name')
    last_name = serializers.CharField(source='profile.last_name')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class WorkPlanTitleDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPlanTitle
        fields = ['id', 'title']

class WorkPlanSerializer(serializers.ModelSerializer):
    titles = WorkPlanTitleSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)  
    coworkers = serializers.SerializerMethodField()

    class Meta:
        model = WorkPlan
        fields = ['id', 'titles', 'description', 'status', 'date', 'created_at', 'created_by', 'coworkers']

    def get_coworkers(self, obj):
        return [
            {"id": u.id, "username": u.username, "email": u.email}
            for u in obj.coworkers.all()
        ]

class WorkPlanCreateSerializer(serializers.ModelSerializer):
    titles = serializers.PrimaryKeyRelatedField(
        many=True, queryset=WorkPlanTitle.objects.all()
    )
    coworkers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = WorkPlan
        fields = ['titles', 'description', 'status', 'coworkers', 'date']

    def create(self, validated_data):
        coworkers = validated_data.pop('coworkers', [])
        titles = validated_data.pop('titles', [])
        user = self.context['request'].user
        workplan = WorkPlan.objects.create(
            created_by=user,
            type='user_created',
            **validated_data
        )
        if coworkers:
            workplan.coworkers.set(coworkers)
        if titles:
            workplan.titles.set(titles)
        return workplan

    def to_representation(self, instance):
        return WorkPlanSerializer(instance, context=self.context).data



# Hourly Report serializers 
# -------------------------
# WorkType Serializer
# -------------------------
class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = ['id', 'name', 'created_at', 'updated_at']


# -------------------------
# WorkDetail Serializer
# -------------------------
class WorkDetailSerializer(serializers.ModelSerializer):
    work_type = serializers.PrimaryKeyRelatedField(queryset=WorkType.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), allow_null=True, required=False)

    class Meta:
        model = WorkDetail
        exclude = ['hourly_report']  # will be set in HourlyReportCreateSerializer


# -------------------------
# HourlyReport Serializer (Read)
# -------------------------
class HourlyReportSerializer(serializers.ModelSerializer):
    work_types = WorkTypeSerializer(many=True, read_only=True)
    details = WorkDetailSerializer(many=True, read_only=True)

    class Meta:
        model = HourlyReport
        fields = '__all__'


# -------------------------
# HourlyReport Serializer (Create / Update)
# -------------------------
from .models import DailySummaryReport

class HourlyReportCreateSerializer(serializers.ModelSerializer):
    work_types = serializers.PrimaryKeyRelatedField(queryset=WorkType.objects.all(), many=True)
    details = WorkDetailSerializer(many=True, required=False)  # details optional

    class Meta:
        model = HourlyReport
        fields = [
            'report_date',
            'report_hour',
            'location_latitude',
            'location_longitude',
            'work_done',
            'reason_not_done',
            'work_types',
            'details',
        ]

    # ---------------------------
    # 🔥 VALIDATE BEFORE CREATE
    # ---------------------------
    def validate(self, data):
        user = self.context['request'].user
        report_date = data.get("report_date")

        # ❌ BLOCK HOURLY REPORT IF SUMMARY EXISTS
        if DailySummaryReport.objects.filter(user=user, report_date=report_date).exists():
            raise serializers.ValidationError(
                "A Daily Summary Report already exists for this date. "
                "You cannot add hourly reports."
            )

        return data

    # ---------------------------
    # CREATE
    # ---------------------------
    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        work_types = validated_data.pop('work_types', [])

        report = HourlyReport.objects.create(
            user=self.context['request'].user,
            **validated_data
        )

        report.work_types.set(work_types)

        for detail_data in details_data:
            WorkDetail.objects.create(hourly_report=report, **detail_data)

        return report

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        work_types = validated_data.pop('work_types', None)

        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update work types
        if work_types is not None:
            instance.work_types.set(work_types)

        # Update details
        if details_data is not None:
            instance.details.all().delete()
            for detail_data in details_data:
                WorkDetail.objects.create(hourly_report=instance, **detail_data)

        return instance

    # Nested output
    def to_representation(self, instance):
        return HourlyReportSerializer(instance, context=self.context).data

class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummaryReport
        fields = [
            'id',
            'report_date',
            'summary_text',
            'total_hours',
        ]

    def validate(self, data):
        user = self.context['request'].user
        report_date = data.get('report_date')

        # ❌ Block summary if hourly reports exist
        if HourlyReport.objects.filter(user=user, report_date=report_date).exists():
            raise serializers.ValidationError(
                "Hourly Reports already exist for this date. Daily Summary is not allowed."
            )

        return data

    def create(self, validated_data):
        return DailySummaryReport.objects.create(
            user=self.context['request'].user,
            **validated_data
        )


class ProjectSerializer(serializers.ModelSerializer):
    remaining_plots = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = '__all__'


# admin_section/serializers.py

from rest_framework import serializers
from admin_section.models import Incentive

class IncentiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incentive
        fields = '__all__'
