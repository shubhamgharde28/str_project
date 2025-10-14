# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

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


from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

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

from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ('user',)



from rest_framework import serializers
from admin_section.models import MonthlyTarget, Sale
from django.contrib.auth.models import User

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


from rest_framework import serializers
from .models import Attendance, UserProfile

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

from rest_framework import serializers
from .models import WorkPlan, WorkPlanTitle
from django.contrib.auth.models import User


from rest_framework import serializers
from django.contrib.auth.models import User
from .models import WorkPlan, WorkPlanTitle


class WorkPlanTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPlanTitle
        fields = ['id', 'title', 'description']


class WorkPlanSerializer(serializers.ModelSerializer):
    titles = WorkPlanTitleSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)  # shows username
    coworkers = serializers.SerializerMethodField()

    class Meta:
        model = WorkPlan
        fields = ['id', 'titles', 'description', 'status', 'date', 'created_at', 'created_by', 'coworkers']

    def get_coworkers(self, obj):
        # Return detailed coworker info (id, username, email)
        return [
            {"id": u.id, "username": u.username, "email": u.email}
            for u in obj.coworkers.all()
        ]


class WorkPlanCreateSerializer(serializers.ModelSerializer):
    # Accept titles as IDs and coworkers as IDs during creation
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

    # <-- this makes the POST response use the full nested WorkPlanSerializer representation
    def to_representation(self, instance):
        return WorkPlanSerializer(instance, context=self.context).data

from rest_framework import serializers
from .models import HourlyReport, WorkDetail, WorkType, WorkTypeOption

class WorkTypeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTypeOption
        fields = ['id', 'name', 'description']

class WorkTypeSerializer(serializers.ModelSerializer):
    options = WorkTypeOptionSerializer(many=True, read_only=True)

    class Meta:
        model = WorkType
        fields = ['id', 'name', 'description', 'options']

from rest_framework import serializers
from .models import WorkDetail, WorkTypeOption

class WorkDetailSerializer(serializers.ModelSerializer):
    work_type_option = serializers.PrimaryKeyRelatedField(queryset=WorkTypeOption.objects.all())

    class Meta:
        model = WorkDetail
        # Exclude hourly_report from input, will assign it in create()
        exclude = ['hourly_report']


class HourlyReportSerializer(serializers.ModelSerializer):
    work_types = WorkTypeSerializer(many=True, read_only=True)
    work_type_options = WorkTypeOptionSerializer(many=True, read_only=True)
    details = WorkDetailSerializer(many=True, read_only=True)

    class Meta:
        model = HourlyReport
        fields = '__all__'

from rest_framework import serializers
from .models import HourlyReport, WorkDetail, WorkType, WorkTypeOption

class HourlyReportCreateSerializer(serializers.ModelSerializer):
    work_types = serializers.PrimaryKeyRelatedField(queryset=WorkType.objects.all(), many=True)
    work_type_options = serializers.PrimaryKeyRelatedField(queryset=WorkTypeOption.objects.all(), many=True)
    details = WorkDetailSerializer(many=True)

    class Meta:
        model = HourlyReport
        fields = ['report_date', 'report_hour', 'location_latitude', 'location_longitude',
                  'work_done', 'reason_not_done', 'work_types', 'work_type_options', 'details']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        work_types_data = validated_data.pop('work_types', [])
        work_type_options_data = validated_data.pop('work_type_options', [])

        # Create HourlyReport instance
        report = HourlyReport.objects.create(user=self.context['request'].user, **validated_data)
        report.work_types.set(work_types_data)
        report.work_type_options.set(work_type_options_data)

        # Create WorkDetail instances and link to HourlyReport
        for detail_data in details_data:
            WorkDetail.objects.create(hourly_report=report, **detail_data)

        return report


