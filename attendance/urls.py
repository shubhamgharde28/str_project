from django.urls import path, include


from .views import SignupView, VerifyOTPView, LoginView, ResendOTPView,CompleteProfileView, UserTargetStatusAPI, AttendanceCheckInView, AttendanceCheckOutView, UserWorkPlanListCreateView, UserWorkPlanDetailView, UserWorkPlanAllView, HourlyReportCreateView, HourlyReportListView, PendingHourlyReportCheckView


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

    path('attendance/check-in/', AttendanceCheckInView.as_view(), name='attendance-check-in'),
    path('attendance/check-out/', AttendanceCheckOutView.as_view(), name='attendance-check-out'),

    path('workplans/user/', UserWorkPlanListCreateView.as_view(), name='user-workplans'),
    path('workplans/user/<int:pk>/', UserWorkPlanDetailView.as_view(), name='user-workplan-detail'),
    path('workplans/user/all/', UserWorkPlanAllView.as_view(), name='user-workplans-all'),


    path('hourly-reports/', HourlyReportListView.as_view(), name='hourly-report-list'),
    path('hourly-reports/create/', HourlyReportCreateView.as_view(), name='hourly-report-create'),
    path('hourly-reports/pending/', PendingHourlyReportCheckView.as_view(), name='hourly-report-pending'),

   ]
