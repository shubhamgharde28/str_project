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





# attendance/models.py
from django.db import models
from django.contrib.auth.models import User

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} ({self.object_id})"

