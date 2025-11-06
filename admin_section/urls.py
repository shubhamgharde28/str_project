from django.urls import path
from . import views

urlpatterns = [
    # MonthlyTarget CRUD
    path('target_and_sale_dashboard/', views.target_and_sale_dashboard, name='target-sale-dashboard'),

    path('targets/', views.target_list, name='target-list'),
    path('targets/create/', views.target_create, name='target-create'),
    path('targets/<int:pk>/update/', views.target_update, name='target-update'),
    path('targets/<int:pk>/delete/', views.target_delete, name='target-delete'),


    # Sale CRUD
    path('sales/', views.sale_list, name='sale-list'),
    path('sales/create/', views.sale_create, name='sale-create'),
    path('sales/<int:pk>/update/', views.sale_update, name='sale-update'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale-delete'),
    path('user/<int:user_id>/target-status/', views.user_target_status, name='user-target-status'),

    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('users/', views.user_list_view, name='user_list'),
    path('users/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('users/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('users/<int:user_id>/edit/', views.edit_user_profile, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    path('monthly_attendance/', views.monthly_attendance, name='monthly_attendance'),
    path('daily_attendance_dashboard/', views.daily_attendance_dashboard, name='daily_attendance_dashboard'),


    path('workplan_dashboard/', views.workplan_dashboard, name='workplan_dashboard'),

    # WorkPlanTitle URLs (Admin only)
    path('dashboard/workplantitles/', views.workplantitle_list, name='workplantitle_list'),
    path('dashboard/workplantitles/create/', views.workplantitle_create, name='workplantitle_create'),
    path('dashboard/workplantitles/edit/<int:pk>/', views.workplantitle_edit, name='workplantitle_edit'),
    path('dashboard/workplantitles/delete/<int:pk>/', views.workplantitle_delete, name='workplantitle_delete'),


    # Admin WorkPlans
    path('workplans/admin/', views.admin_workplan_list, name='admin_workplan_list'),
    path('workplans/admin/create/', views.admin_workplan_create, name='admin_workplan_create'),
    path('workplans/admin/edit/<int:pk>/', views.admin_workplan_edit, name='admin_workplan_edit'),
    path('workplans/admin/delete/<int:pk>/', views.admin_workplan_delete, name='admin_workplan_delete'),

    # User WorkPlans
    path('workplans/user/', views.user_workplan_list, name='user_workplan_list'),
    path('workplans/user/create/', views.user_workplan_create, name='user_workplan_create'),
    path('workplans/user/edit/<int:pk>/', views.user_workplan_edit, name='user_workplan_edit'),
    path('workplans/user/delete/<int:pk>/', views.user_workplan_delete, name='user_workplan_delete'),

    # WorkType URLs
    path('worktypes/', views.worktype_list, name='worktype_list'),
    path('worktypes/create/', views.worktype_create, name='worktype_create'),
    path('worktypes/<int:pk>/edit/', views.worktype_edit, name='worktype_edit'),
    path('worktypes/<int:pk>/delete/', views.worktype_delete, name='worktype_delete'),

    # HourlyReport URLs
    path('hourlyreports/', views.hourlyreport_list, name='hourlyreport_list'),
    path('hourlyreports/create/', views.hourlyreport_create, name='hourlyreport_create'),
    path('hourlyreports/<int:pk>/edit/', views.hourlyreport_edit, name='hourlyreport_edit'),

    # WorkDetail URLs
    path('workdetails/', views.workdetail_list, name='workdetail_list'),
    path('workdetails/create/', views.workdetail_create, name='workdetail_create'),
    path('workdetails/<int:pk>/edit/', views.workdetail_edit, name='workdetail_edit'),

    path('dashboard/reports/', views.report_dashboard, name='report_dashboard'),




]
