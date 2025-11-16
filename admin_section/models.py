from django.db import models
from django.contrib.auth.models import User

MONTH_CHOICES = [
    (1, "January"), (2, "February"), (3, "March"), (4, "April"),
    (5, "May"), (6, "June"), (7, "July"), (8, "August"),
    (9, "September"), (10, "October"), (11, "November"), (12, "December")
]

class MonthlyTarget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_targets')
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    target_area = models.FloatField(default=1500)  # sq ft target
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
    area_sold = models.FloatField()  # sq ft sold

    class Meta:
        unique_together = ('user', 'month', 'year')  # ek user ke liye ek month ek hi sale
        ordering = ['year', 'month']

    def __str__(self):
        return f"{self.user.email} - {self.get_month_display()} {self.year} sold {self.area_sold} sq ft"


# models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import time

# salary/models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import time

class SalaryConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salary_config')

    # Pay
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, help_text="Monthly gross salary")
    working_days = models.PositiveIntegerField(default=26, help_text="Working days used to compute per-day salary")

    # Late rules
    late_mark_after = models.TimeField(default=time(9, 30), help_text="After this time check-in considered late")
    half_day_after_minutes = models.PositiveIntegerField(default=15, help_text="Late minutes after which half-day applies")
    late_deduction_per_minute = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Per-minute late deduction (optional)")

    # Early leave rules
    early_leave_before = models.TimeField(default=time(17, 0), help_text="If checkout before this time considered early")
    early_leave_minutes = models.PositiveIntegerField(default=0, help_text="Early minutes threshold to count half-day")
    early_leave_deduction_per_minute = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Per-minute early deduction (optional)")

    # Leaves & target penalty
    allowed_leaves = models.PositiveIntegerField(default=4, help_text="Number of paid leaves allowed per month")
    target_penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Penalty if monthly target not met")

    def daily_salary(self):
        """
        Per-day salary = monthly_salary / working_days (dynamic)
        """
        try:
            if self.working_days and int(self.working_days) > 0:
                return self.monthly_salary / self.working_days
        except Exception:
            pass
        return 0

    def __str__(self):
        return f"{self.user.username} SalaryConfig"


