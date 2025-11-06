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



