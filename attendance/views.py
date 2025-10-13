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

