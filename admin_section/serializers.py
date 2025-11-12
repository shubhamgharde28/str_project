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

