from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, VerifyOTPView, LoginView, ResendOTPView,CompleteProfileView, UserTargetStatusAPI, AttendanceCheckInView, AttendanceCheckOutView, UserWorkPlanListCreateView, UserWorkPlanDetailView, UserWorkPlanAllView, HourlyReportCreateView, HourlyReportListView, MonthlyAttendanceSummaryView, TargetSummaryView, WorkPlanDropdownsAPIView, WorkTypeListAPIView, WorkPlanTitleListAPIView, ProjectListAPIView, LogoutView, UserSalarySlipViewSet, SimpleHourlyReportCheckAPI, HourlyReportUpdateView, DailySummaryCreateView, DailySummaryListView, DailySummaryUpdateView, UserIncentiveViewSet

router = DefaultRouter()
router.register(r"user-salary-slip", UserSalarySlipViewSet, basename="user-salary-slip")
router.register('my-incentives', UserIncentiveViewSet, basename='my-incentives')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('profile/complete/', CompleteProfileView.as_view(), name='profile-complete'),

    path('user/<int:user_id>/target-status/', UserTargetStatusAPI.as_view(), name='api-user-target-status'),
    path('user/<int:user_id>/target-status/<int:year>/', UserTargetStatusAPI.as_view(), name='api-user-target-status-year'),

    path('attendance/check-in/', AttendanceCheckInView.as_view(), name='attendance-check-in'),
    path('attendance/check-out/', AttendanceCheckOutView.as_view(), name='attendance-check-out'),
    path('attendance/summary/', MonthlyAttendanceSummaryView.as_view(), name='attendance-summary'),

    path('target/summary/', TargetSummaryView.as_view(), name='target-summary'),

    path('workplans/user/', UserWorkPlanListCreateView.as_view(), name='user-workplans'),
    path('workplans/user/<int:pk>/', UserWorkPlanDetailView.as_view(), name='user-workplan-detail'),
    path('workplans/user/all/', UserWorkPlanAllView.as_view(), name='user-workplans-all'),
    path('workplan/dropdowns/', WorkPlanDropdownsAPIView.as_view(), name='workplan-dropdowns'),
    path('workplan-titles/', WorkPlanTitleListAPIView.as_view(), name='workplan-title-list'),
    path('projects/', ProjectListAPIView.as_view(), name='projects-list'),

    path('work-types/', WorkTypeListAPIView.as_view(), name='work-type-list'),
    path('hourly-reports/', HourlyReportListView.as_view(), name='hourly-report-list'),
    path('hourly-reports/create/', HourlyReportCreateView.as_view(), name='hourly-report-create'),
    path('hourly-reports/update/<int:pk>/', HourlyReportUpdateView.as_view(), name='hourly-report-update'),

    path("summary/create/", DailySummaryCreateView.as_view()),
    path("summary/list/", DailySummaryListView.as_view()),
    path("summary/update/<int:pk>/", DailySummaryUpdateView.as_view()),

    path("simple-hourly-check/", SimpleHourlyReportCheckAPI.as_view()),



]
