# admin_section/models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import time

MONTH_CHOICES = [
    (1, "January"), (2, "February"), (3, "March"), (4, "April"),
    (5, "May"), (6, "June"), (7, "July"), (8, "August"),
    (9, "September"), (10, "October"), (11, "November"), (12, "December")
]

class MonthlyTarget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_targets')
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    target_area = models.FloatField(default=1500)  
    carry_forward = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'month', 'year')
        ordering = ['year', 'month']

    def __str__(self):
        return f"{self.user.email} - {self.get_month_display()} {self.year}"

class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    area_sold = models.FloatField()  

    class Meta:
        unique_together = ('user', 'month', 'year')  
        ordering = ['year', 'month']

    def __str__(self):
        return f"{self.user.email} - {self.get_month_display()} {self.year} sold {self.area_sold} sq ft"

class SalaryConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salary_config')
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    working_days = models.PositiveIntegerField(default=26)
    late_allowed_time = models.TimeField(default=time(9, 0))   # after this -> late
    early_leave_allowed_time = models.TimeField(default=time(17, 0)) 
    target_area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    target_penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def daily_salary(self):
        try:
            wd = int(self.working_days)
            if wd <= 0:
                return 0
            return (self.monthly_salary / wd)
        except Exception:
            return 0

    def __str__(self):
        return f"Salary Config for {self.user.username}"
