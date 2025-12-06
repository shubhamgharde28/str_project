# admin_section/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonthlyTargetViewSet, SaleViewSet, UserTargetStatusViewSet, TargetAndSaleDashboardViewSet, AdminUserViewSet, AttendanceDashboardViewSet, WorkPlanTitleViewSet, AdminWorkPlanViewSet, UserWorkPlanViewSet, WorkTypeViewSet, HourlyReportViewSet, WorkDetailViewSet, DashboardViewSet, SalaryConfigViewSet, ProjectViewSet, DailySummaryViewSet_admin

router = DefaultRouter()

router.register(r'projects-admin', ProjectViewSet, basename='projects-admin')

router.register(r'targets', MonthlyTargetViewSet, basename='target')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'user-target-status', UserTargetStatusViewSet, basename='user-target-status')
router.register(r'target-sale-dashboard', TargetAndSaleDashboardViewSet, basename='target-sale-dashboard')
router.register('users', AdminUserViewSet, basename='admin-users')
router.register(r'attendance-dashboard', AttendanceDashboardViewSet, basename='attendance-dashboard')
router.register(r'workplan-titles', WorkPlanTitleViewSet, basename='workplan-titles')
router.register(r'admin-workplans', AdminWorkPlanViewSet, basename='admin-workplans')
router.register(r'user-workplans', UserWorkPlanViewSet, basename='user-workplans')
router.register(r'worktypes', WorkTypeViewSet, basename='worktype')

router.register(r'hourly-reports', HourlyReportViewSet, basename='hourlyreport')
router.register(r'work-details', WorkDetailViewSet, basename='workdetail')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'salary', SalaryConfigViewSet, basename='salary')
router.register('daily-summaries', DailySummaryViewSet_admin, basename='admin-daily-summaries')

urlpatterns = [
    path('', include(router.urls)),
]
