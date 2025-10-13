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
from .models import UserProfile

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
