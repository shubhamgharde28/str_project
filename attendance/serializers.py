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




