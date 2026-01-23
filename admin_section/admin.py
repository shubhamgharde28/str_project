from django.contrib import admin
from .models import ContactUs, MonthlyTarget, Sale, SalaryConfig, Incentive

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at', 'replied_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Admin Reply', {
            'fields': ('admin_reply', 'replied_by', 'replied_at')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(MonthlyTarget)
class MonthlyTargetAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'target_area')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'area_sold')

@admin.register(SalaryConfig)
class SalaryConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'monthly_salary', 'working_days')

@admin.register(Incentive)
class IncentiveAdmin(admin.ModelAdmin):
    list_display = ('user', 'plot_number', 'total_price', 'commission_price', 'balance_commission')

