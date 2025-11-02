from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Unregister default User admin
admin.site.unregister(User)

# Now register your custom UserAdmin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) successfully approved.")
    approve_users.short_description = "Approve selected users"

admin.site.register(User, UserAdmin)


from django.contrib import admin
from .models import UserProfile, Attendance


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'first_name', 'last_name', 'designation', 'department',
        'mobile_number', 'city', 'state', 'gender', 'marital_status', 'created_at'
    )
    search_fields = ('user__email', 'first_name', 'last_name', 'mobile_number', 'aadhaar_number', 'pan_number')
    list_filter = ('department', 'designation', 'gender', 'marital_status', 'city', 'state')
    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'



@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'first_name', 'last_name', 'date', 
        'check_in_time', 'check_out_time', 'check_in_latitude', 'check_in_longitude'
    )
    search_fields = ('user__email', 'user__profile__first_name', 'user__profile__last_name')
    list_filter = ('date',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'

    def first_name(self, obj):
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.first_name
        return ''
    
    def last_name(self, obj):
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.last_name
        return ''
    

from django.contrib import admin
from .models import WorkPlan, WorkPlanTitle, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'project_type',
        'city',
        'state',
        'total_plots',
        'sold_plots',
        'remaining_plots',
        'is_active',
        'created_at'
    )
    list_filter = ('project_type', 'city', 'state', 'is_active')
    search_fields = ('name', 'city', 'state')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Project Information', {
            'fields': (
                'name',
                'project_type',
                'description',
                'created_by'
            )
        }),
        ('Plot Details', {
            'fields': (
                'total_plots',
                'sold_plots',
                'available_plots'
            )
        }),
        ('Location Information', {
            'fields': (
                'address',
                'city',
                'state',
                'pincode'
            )
        }),
        ('Timeline', {
            'fields': (
                'launch_date',
                'expected_completion_date'
            )
        }),
        ('Status & Timestamps', {
            'fields': (
                'is_active',
                'created_at',
                'updated_at'
            )
        }),
    )



@admin.register(WorkPlanTitle)
class WorkPlanTitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description')
    search_fields = ('title',)


@admin.register(WorkPlan)
class WorkPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'date', 'status', 'type')
    list_filter = ('status', 'type', 'date')
    search_fields = ('description',)
    filter_horizontal = ('coworkers', 'titles')



from django.contrib import admin
from .models import WorkType, WorkTypeOption, HourlyReport, WorkDetail

# Inline for WorkTypeOption under WorkType
class WorkTypeOptionInline(admin.TabularInline):
    model = WorkTypeOption
    extra = 1  # Number of empty fields
    show_change_link = True

@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    inlines = [WorkTypeOptionInline]

# Inline for WorkDetail under HourlyReport
class WorkDetailInline(admin.TabularInline):
    model = WorkDetail
    extra = 1
    show_change_link = True

@admin.register(HourlyReport)
class HourlyReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_date', 'report_hour', 'work_done', 'created_at']
    list_filter = ['report_date', 'report_hour', 'work_done']
    search_fields = ['user__username', 'user__email']
    inlines = [WorkDetailInline]
    filter_horizontal = ['work_types', 'work_type_options']  # For ManyToMany fields

@admin.register(WorkTypeOption)
class WorkTypeOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'work_type', 'description']
    list_filter = ['work_type']
    search_fields = ['name', 'work_type__name']

@admin.register(WorkDetail)
class WorkDetailAdmin(admin.ModelAdmin):
    list_display = ('hourly_report', 'project', 'work_type_option', 'customer_name', 'customer_response', 'next_followup_date')
    list_filter = ('project', 'customer_response',)
    search_fields = ('customer_name', 'mobile_number', 'project__name')

