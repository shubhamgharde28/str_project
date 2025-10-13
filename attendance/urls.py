from django.urls import path
from .views import SignupView, VerifyOTPView, LoginView, ResendOTPView,CompleteProfileView, UserTargetStatusAPI

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('profile/complete/', CompleteProfileView.as_view(), name='profile-complete'),

    path('user/<int:user_id>/target-status/', UserTargetStatusAPI.as_view(), name='api-user-target-status'),
    path('user/<int:user_id>/target-status/<int:year>/', UserTargetStatusAPI.as_view(), name='api-user-target-status-year'),

   ]
