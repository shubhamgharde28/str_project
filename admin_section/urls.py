from django.urls import path
from . import views
# attendance/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonthlyTargetViewSet, SaleViewSet, UserTargetStatusViewSet

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonthlyTargetViewSet, SaleViewSet, UserTargetStatusViewSet, TargetAndSaleDashboardViewSet, AdminUserViewSet, AttendanceDashboardViewSet, WorkPlanTitleViewSet, AdminWorkPlanViewSet, UserWorkPlanViewSet, WorkTypeViewSet, WorkTypeOptionViewSet, HourlyReportViewSet, WorkDetailViewSet, DashboardViewSet, SalaryConfigViewSet










router = DefaultRouter()

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
router.register(r'worktype-options', WorkTypeOptionViewSet, basename='worktypeoption')
router.register(r'hourly-reports', HourlyReportViewSet, basename='hourlyreport')
router.register(r'work-details', WorkDetailViewSet, basename='workdetail')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'salary', SalaryConfigViewSet, basename='salary')

urlpatterns = [
    path('', include(router.urls)),









    # MonthlyTarget CRUD
    path('MVT-target_and_sale_dashboard/', views.target_and_sale_dashboard, name='target-sale-dashboard'),

    path('MVT-targets/', views.target_list, name='target-list'),
    path('MVT-targets/create/', views.target_create, name='target-create'),
    path('MVT-targets/<int:pk>/update/', views.target_update, name='target-update'),
    path('MVT-targets/<int:pk>/delete/', views.target_delete, name='target-delete'),


    # Sale CRUD
    path('MVT-sales/', views.sale_list, name='sale-list'),
    path('MVT-sales/create/', views.sale_create, name='sale-create'),
    path('MVT-sales/<int:pk>/update/', views.sale_update, name='sale-update'),
    path('MVT-sales/<int:pk>/delete/', views.sale_delete, name='sale-delete'),
    path('MVT-user/<int:user_id>/target-status/', views.user_target_status, name='user-target-status'),

    path('MVT-dashboard/', views.dashboard_view, name='dashboard'),

    path('MVT-users/', views.user_list_view, name='user_list'),
    path('MVT-users/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('MVT-users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('MVT-users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('MVT-users/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('MVT-users/<int:user_id>/edit/', views.edit_user_profile, name='edit_user'),
    path('MVT-users/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    path('MVT-monthly_attendance/', views.monthly_attendance, name='monthly_attendance'),
    path('MVT-daily_attendance_dashboard/', views.daily_attendance_dashboard, name='daily_attendance_dashboard'),


    path('MVT-workplan_dashboard/', views.workplan_dashboard, name='workplan_dashboard'),

    # WorkPlanTitle URLs (Admin only)
    path('MVT-dashboard/workplantitles/', views.workplantitle_list, name='workplantitle_list'),
    path('MVT-dashboard/workplantitles/create/', views.workplantitle_create, name='MVT-workplantitle_create'),
    path('MVT-dashboard/workplantitles/edit/<int:pk>/', views.workplantitle_edit, name='workplantitle_edit'),
    path('MVT-dashboard/workplantitles/delete/<int:pk>/', views.workplantitle_delete, name='workplantitle_delete'),


    # Admin WorkPlans
    path('MVT-workplans/admin/', views.admin_workplan_list, name='admin_workplan_list'),
    path('MVT-workplans/admin/create/', views.admin_workplan_create, name='admin_workplan_create'),
    path('MVT-workplans/admin/edit/<int:pk>/', views.admin_workplan_edit, name='admin_workplan_edit'),
    path('MVT-workplans/admin/delete/<int:pk>/', views.admin_workplan_delete, name='admin_workplan_delete'),

    # User WorkPlans
    path('MVT-workplans/user/', views.user_workplan_list, name='user_workplan_list'),
    path('MVT-workplans/user/create/', views.user_workplan_create, name='user_workplan_create'),
    path('MVT-workplans/user/edit/<int:pk>/', views.user_workplan_edit, name='user_workplan_edit'),
    path('MVT-workplans/user/delete/<int:pk>/', views.user_workplan_delete, name='user_workplan_delete'),

    # WorkType URLs
    path('MVT-worktypes/', views.worktype_list, name='worktype_list'),
    path('MVT-worktypes/create/', views.worktype_create, name='worktype_create'),
    path('MVT-worktypes/<int:pk>/edit/', views.worktype_edit, name='worktype_edit'),
    path('MVT-worktypes/<int:pk>/delete/', views.worktype_delete, name='worktype_delete'),

    # HourlyReport URLs
    path('MVT-hourlyreports/', views.hourlyreport_list, name='hourlyreport_list'),
    path('MVT-hourlyreports/create/', views.hourlyreport_create, name='hourlyreport_create'),
    path('MVT-hourlyreports/<int:pk>/edit/', views.hourlyreport_edit, name='hourlyreport_edit'),

    # WorkDetail URLs
    path('MVT-workdetails/', views.workdetail_list, name='workdetail_list'),
    path('MVT-workdetails/create/', views.workdetail_create, name='workdetail_create'),
    path('MVT-workdetails/<int:pk>/edit/', views.workdetail_edit, name='workdetail_edit'),

    path('MVT-dashboard/reports/', views.report_dashboard, name='report_dashboard'),




]
