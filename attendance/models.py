# models.py
from django.db import models
from django.contrib.auth.models import User

# Optional — if you want to keep record of OTPs
class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"


from django.db import models
from django.contrib.auth.models import User

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

MARITAL_STATUS_CHOICES = (
    ('single', 'Single'),
    ('married', 'Married'),
    ('divorced', 'Divorced'),
    ('widowed', 'Widowed'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    aadhaar_number = models.CharField(max_length=12)
    pan_number = models.CharField(max_length=10)
    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Profile"


from django.db import models
from django.contrib.auth.models import User


from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('mixed_use', 'Mixed Use'),
        ('plotting', 'Plotting'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    name = models.CharField(max_length=150, unique=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='plotting')
    description = models.TextField(blank=True, null=True)
    
    total_plots = models.PositiveIntegerField(default=0)
    available_plots = models.PositiveIntegerField(default=0)
    sold_plots = models.PositiveIntegerField(default=0)

    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    launch_date = models.DateField(blank=True, null=True)
    expected_completion_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return f"{self.name} ({self.city})"

    @property
    def remaining_plots(self):
        return self.total_plots - self.sold_plots



class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_in_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    check_in_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    check_out_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    check_out_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"


from django.db import models
from django.contrib.auth.models import User


class WorkPlanTitle(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class WorkPlan(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
    ]

    TYPE_CHOICES = [
        ('user_created', 'User Created'),
        ('admin_created', 'Admin Created'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workplans')
    coworkers = models.ManyToManyField(User, related_name='shared_workplans', blank=True)
    titles = models.ManyToManyField(WorkPlanTitle, related_name='workplans')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='user_created')
    date = models.DateField()  # 🟢 Now user will manually select this date
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_by.username} ({self.date})"



from django.db import models
from django.contrib.auth.models import User

# Customer response choices
CUSTOMER_RESPONSE_CHOICES = [
    ('interested', 'Interested'),
    ('not_interested', 'Not Interested'),
    ('not_sure', 'Not Sure')
]

# Yes/No choice
YES_NO_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No')
]

class WorkType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class WorkTypeOption(models.Model):
    work_type = models.ForeignKey(WorkType, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.work_type.name} - {self.name}"

class HourlyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hourly_reports')
    report_date = models.DateField()  # Date of the report
    report_hour = models.IntegerField()  # Hour 0-23
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    work_done = models.CharField(max_length=3, choices=YES_NO_CHOICES)
    reason_not_done = models.TextField(blank=True, null=True)

    # Work types and options selected
    work_types = models.ManyToManyField(WorkType, blank=True, related_name='hourly_reports')
    work_type_options = models.ManyToManyField(WorkTypeOption, blank=True, related_name='hourly_reports')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.report_date} - Hour {self.report_hour}"

class WorkDetail(models.Model):
    hourly_report = models.ForeignKey(HourlyReport, on_delete=models.CASCADE, related_name='details')
    work_type_option = models.ForeignKey(WorkTypeOption, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='work_details', null=True, blank=True)  # ✅ NEW FIELD

    customer_name = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    plot_number = models.CharField(max_length=50, blank=True, null=True)
    
    customer_response = models.CharField(max_length=15, choices=CUSTOMER_RESPONSE_CHOICES)
    reason_not_interested = models.TextField(blank=True, null=True)

    site_visit_done = models.BooleanField(default=False)
    meeting_done = models.BooleanField(default=False)
    booking_done = models.BooleanField(default=False)
    next_followup_date = models.DateField(blank=True, null=True)

    def __str__(self):
        project_name = self.project.name if self.project else "No Project"
        return f"{self.hourly_report} - {project_name} - {self.work_type_option.name}"