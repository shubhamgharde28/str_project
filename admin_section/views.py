from django.shortcuts import render, redirect, get_object_or_404
from .models import MonthlyTarget, Sale
from .forms import MonthlyTargetForm, SaleForm
from django.contrib import messages

# ------------------ MonthlyTarget CRUD ------------------

def target_list(request):
    targets = MonthlyTarget.objects.all().order_by('year', 'month')
    return render(request, 'targets/target_list.html', {'targets': targets})

def target_create(request):
    if request.method == 'POST':
        form = MonthlyTargetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Monthly Target created successfully.')
            return redirect('target-list')
    else:
        form = MonthlyTargetForm()
    return render(request, 'targets/target_form.html', {'form': form, 'title': 'Create Target'})

def target_update(request, pk):
    target = get_object_or_404(MonthlyTarget, pk=pk)
    if request.method == 'POST':
        form = MonthlyTargetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, 'Monthly Target updated successfully.')
            return redirect('target-list')
    else:
        form = MonthlyTargetForm(instance=target)
    return render(request, 'targets/target_form.html', {'form': form, 'title': 'Update Target'})

def target_delete(request, pk):
    target = get_object_or_404(MonthlyTarget, pk=pk)
    if request.method == 'POST':
        target.delete()
        messages.success(request, 'Monthly Target deleted successfully.')
        return redirect('target-list')
    return render(request, 'targets/target_confirm_delete.html', {'target': target})

# ------------------ Sale CRUD ------------------

from django.shortcuts import render, redirect, get_object_or_404
from .models import Sale
from .forms import SaleForm
from django.contrib import messages

def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale created successfully.')
            return redirect('sale-list')
    else:
        form = SaleForm()
    return render(request, 'sales/sale_form.html', {'form': form, 'title': 'Create Sale'})

def sale_list(request):
    sales = Sale.objects.all().order_by('year', 'month')
    return render(request, 'sales/sale_list.html', {'sales': sales})

def sale_update(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully.')
            return redirect('sale-list')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sales/sale_form.html', {'form': form, 'title': 'Update Sale'})

def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Sale deleted successfully.')
        return redirect('sale-list')
    return render(request, 'sales/sale_confirm_delete.html', {'sale': sale})



from django.shortcuts import render, get_object_or_404
from .models import MonthlyTarget, Sale
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import date

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import MonthlyTarget, Sale
from datetime import date

from django.shortcuts import render
from django.contrib.auth.models import User
from .models import MonthlyTarget, Sale
from django.db.models import Sum
from datetime import date

from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import MonthlyTarget, Sale
from datetime import date



def user_target_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    year = date.today().year  # you can also allow selecting year dynamically
    targets = MonthlyTarget.objects.filter(user=user, year=year).order_by('month')

    monthly_status = []
    carry_forward = 0  # start with 0

    for target in targets:
        # Total sold in this month from Sale model with month/year fields
        sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
        total_sold = sales['total_sold'] or 0

        # Effective sold including carry-forward from previous month
        effective_sold = total_sold + carry_forward

        # Check if target is achieved
        if effective_sold >= target.target_area:
            status = 'green'  # Target met
            carry_forward = effective_sold - target.target_area  # carry excess to next month
        else:
            status = 'red'  # Target not met
            carry_forward = 0  # No carry forward if target not met

        monthly_status.append({
            'month': target.get_month_display(),
            'target_area': target.target_area,
            'sold_area': total_sold,
            'status': status,
            'carry_forward': carry_forward
        })

    return render(request, 'targets/user_target_status.html', {
        'user': user,
        'monthly_status': monthly_status,
        'year': year
    })



from django.shortcuts import render
from .models import MonthlyTarget, Sale
from django.contrib.auth.models import User
from django.db.models import Sum

from django.contrib.auth.models import User
from datetime import date
from django.db.models import Sum
from .models import MonthlyTarget, Sale
from django.shortcuts import render

def target_and_sale_dashboard(request):
    # Get year and month from GET params, fallback to current date
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = request.GET.get('month')
    if month:
        month = int(month)
    
    total_targets = MonthlyTarget.objects.filter(year=year)
    total_sales = Sale.objects.filter(year=year)
    total_users = User.objects.exclude(is_superuser=True).count()

    total_target_area = total_targets.aggregate(total=Sum('target_area'))['total'] or 0
    total_sold_area = total_sales.aggregate(total=Sum('area_sold'))['total'] or 0

    progress_percent = round((total_sold_area / total_target_area) * 100, 2) if total_target_area else 0.0

    users_status = []
    users = User.objects.exclude(is_superuser=True).order_by('username')
    for user in users:
        user_targets = MonthlyTarget.objects.filter(user=user, year=year)
        if month:
            user_targets = user_targets.filter(month=month)
        user_targets = user_targets.order_by('month')

        monthly_status = []
        carry_forward = 0

        for target in user_targets:
            sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
            total_sold = sales['total_sold'] or 0
            effective_sold = total_sold + carry_forward

            if effective_sold >= target.target_area:
                status = 'green'
                carry_forward = effective_sold - target.target_area
            else:
                status = 'red'
                carry_forward = 0

            monthly_status.append({
                'month': target.get_month_display(),
                'target_area': target.target_area,
                'sold_area': total_sold,
                'status': status,
                'carry_forward': carry_forward,
            })

        users_status.append({
            'user': user,
            'monthly_status': monthly_status,
        })

    context = {
        'total_targets': total_targets.count(),
        'total_sales': total_sales.count(),
        'total_users': total_users,
        'total_target_area': total_target_area,
        'total_sold_area': total_sold_area,
        'progress_percent': progress_percent,
        'users_status': users_status,
        'year': year,
        'month': month,
    }
    return render(request, 'targets/target_and_sale_dashboard.html', context)

from django.contrib.auth.models import User
from django.shortcuts import render

from django.utils.timesince import timesince
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render

def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func



from django.utils.timesince import timesince
from django.utils.timezone import now

from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils.timesince import timesince
from datetime import date
from attendance.models import Attendance

from django.shortcuts import render
from django.contrib.auth.models import User
from datetime import date
from attendance.models import Attendance

from django.shortcuts import render
from django.contrib.auth.models import User
from attendance.models import Attendance, WorkPlan
from datetime import date
from django.utils.timesince import timesince
from django.contrib.auth.decorators import user_passes_test


from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from attendance.models import Attendance, WorkPlan
from datetime import date

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def dashboard_view(request):
    today = date.today()

    # Total employees (excluding superusers)
    users = User.objects.exclude(is_superuser=True)
    total_users = users.count()

    # Attendance counts
    checked_in_att = Attendance.objects.filter(date=today, check_in_time__isnull=False).select_related('user')
    checked_in_count = checked_in_att.count()
    not_checked_in_count = total_users - checked_in_count

    # Recent activities list
    recent_activity = []

    def get_user_name(user):
        """Return user's full name even if profile missing."""
        try:
            return f"{user.profile.first_name} {user.profile.last_name}".strip() or user.username
        except Exception:
            return user.username

    # Checked-in users
    for att in checked_in_att:
        recent_activity.append({
            'title': 'Checked In',
            'description': f"{get_user_name(att.user)} checked in at {att.check_in_time.strftime('%I:%M %p')}",
            'time': att.check_in_time.strftime('%H:%M'),
            'user_id': att.user.id,
            'icon': 'fa-sign-in-alt',
            'color': 'var(--success)',
        })

    # Checked-out users
    checked_out_att = Attendance.objects.filter(date=today, check_out_time__isnull=False).select_related('user')
    for att in checked_out_att:
        recent_activity.append({
            'title': 'Checked Out',
            'description': f"{get_user_name(att.user)} checked out at {att.check_out_time.strftime('%I:%M %p')}",
            'time': att.check_out_time.strftime('%H:%M'),
            'user_id': att.user.id,
            'icon': 'fa-sign-out-alt',
            'color': 'var(--primary)',
        })

    # Sort latest activities
    recent_activity = sorted(recent_activity, key=lambda x: x['time'], reverse=True)

    # Workplan stats
    workplans_today = WorkPlan.objects.filter(date=today)
    total_workplans = workplans_today.count()
    completed_workplans = workplans_today.filter(status='completed').count()
    pending_workplans = total_workplans - completed_workplans

    # Admin/User workplan stats
    admin_workplans_count = WorkPlan.objects.filter(type='admin_created').count()
    user_workplans_count = WorkPlan.objects.filter(type='user_created').count()

    context = {
        'total_users': total_users,
        'checked_in_count': checked_in_count,
        'not_checked_in_count': not_checked_in_count,
        'recent_activity': recent_activity,
        'total_workplans': total_workplans,
        'completed_workplans': completed_workplans,
        'pending_workplans': pending_workplans,
        'admin_workplans_count': admin_workplans_count,
        'user_workplans_count': user_workplans_count,
    }

    return render(request, 'dashboard.html', context)





@superuser_required
def user_list_view(request):
    filter_type = request.GET.get('filter', 'all')  # default 'all'

    users = User.objects.all().order_by('-date_joined')

    if filter_type == 'pending':
        users = users.filter(is_active=False, is_superuser=False)
    elif filter_type == 'approved':
        users = users.filter(is_active=True, is_superuser=False)
    elif filter_type == 'admins':
        users = users.filter(is_superuser=True)

    total_users = User.objects.exclude(is_superuser=True).count()
    approved_users = User.objects.filter(is_active=True, is_superuser=False).count()
    pending_users = User.objects.filter(is_active=False, is_superuser=False).count()
    super_users = User.objects.filter(is_superuser=True).count()

    context = {
        'users': users,
        'total_users': total_users,
        'approved_users': approved_users,
        'pending_users': pending_users,
        'super_users': super_users,
        'active_filter': filter_type,
    }
    return render(request, 'user_list.html', context)



@superuser_required
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"{user.username} has been approved successfully.")
    return redirect('user_list')

@superuser_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        user.username = username
        user.email = email
        user.save()
        messages.success(request, f"{user.username} has been updated successfully.")
        return redirect('user_list')
    return render(request, 'edit_user.html', {'user': user})

@superuser_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('user_list')
    return render(request, 'delete_user.html', {'user': user})



# views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

@superuser_required
def user_detail_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, 'profile', None)  # Check if profile exists
    context = {
        'user_obj': user,
        'profile': profile,
    }
    return render(request, 'user_detail.html', context)

@superuser_required
def edit_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, 'profile', None)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        if profile:
            profile.first_name = request.POST.get('first_name')
            profile.last_name = request.POST.get('last_name')
            profile.designation = request.POST.get('designation')
            profile.department = request.POST.get('department')
            profile.mobile_number = request.POST.get('mobile_number')
            profile.gender = request.POST.get('gender')
            profile.marital_status = request.POST.get('marital_status')
            profile.aadhaar_number = request.POST.get('aadhaar_number')
            profile.pan_number = request.POST.get('pan_number')
            profile.locality = request.POST.get('locality')
            profile.city = request.POST.get('city')
            profile.state = request.POST.get('state')
            profile.pincode = request.POST.get('pincode')
            profile.save()
        user.save()
        return redirect('user_detail', user_id=user.id)

    context = {'user_obj': user, 'profile': profile}
    return render(request, 'edit_user_profile.html', context)

@superuser_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_list')















from attendance.models import Attendance

from django.shortcuts import render
from django.contrib.auth.models import User
from datetime import date, timedelta

from datetime import date, datetime, timedelta
import calendar
from django.shortcuts import render
from django.contrib.auth.models import User

def monthly_attendance(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # Get total days in selected month
    total_days = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, total_days)

    users = User.objects.exclude(is_superuser=True).order_by('username')
    attendance_data = []

    for user in users:
        row = {'user': user, 'days': []}

        for day in range(1, total_days + 1):
            current_date = date(year, month, day)
            attendance = Attendance.objects.filter(user=user, date=current_date).first()

            if attendance:
                # ✅ Mark Present
                row['days'].append('P')
            else:
                if current_date > today:
                    # ⏳ Future Date → Not yet completed
                    row['days'].append('-')
                else:
                    # ❌ Past Date but no record → Absent
                    row['days'].append('A')

        attendance_data.append(row)

    context = {
        'attendance_data': attendance_data,
        'month': month,
        'year': year,
        'days_in_month': range(1, total_days + 1),
    }
    return render(request, 'attendance/monthly_attendance.html', context)


from django.shortcuts import render
from datetime import date
from geopy.geocoders import Nominatim

from django.shortcuts import render
from django.contrib.auth.models import User
from datetime import date
from attendance.models import Attendance
from geopy.geocoders import Nominatim

def daily_attendance_dashboard(request):
    today = date.today()
    users = User.objects.exclude(is_superuser=True).order_by('username')

    total_employees = users.count()
    present_count = 0
    absent_count = 0

    geolocator = Nominatim(user_agent="attendance_app")  # geopy

    data = []
    for user in users:
        attendance = Attendance.objects.filter(user=user, date=today).first()

        if attendance and attendance.check_in_time:
            status = 'Present'
            present_count += 1
        else:
            status = 'Absent'
            absent_count += 1

        # Reverse geocode check-in
        if attendance and attendance.check_in_latitude and attendance.check_in_longitude:
            try:
                location_in = geolocator.reverse(
                    f"{attendance.check_in_latitude},{attendance.check_in_longitude}", timeout=10
                )
                check_in_address = location_in.address if location_in else '-'
            except:
                check_in_address = '-'
        else:
            check_in_address = '-'

        # Reverse geocode check-out
        if attendance and attendance.check_out_latitude and attendance.check_out_longitude:
            try:
                location_out = geolocator.reverse(
                    f"{attendance.check_out_latitude},{attendance.check_out_longitude}", timeout=10
                )
                check_out_address = location_out.address if location_out else '-'
            except:
                check_out_address = '-'
        else:
            check_out_address = '-'

        data.append({
            'user': user,
            'status': status,
            'check_in': attendance.check_in_time.strftime("%H:%M:%S") if attendance and attendance.check_in_time else '-',
            'check_in_loc': check_in_address,
            'check_out': attendance.check_out_time.strftime("%H:%M:%S") if attendance and attendance.check_out_time else '-',
            'check_out_loc': check_out_address,
        })

    context = {
        'today': today,
        'total_employees': total_employees,
        'present_count': present_count,
        'absent_count': absent_count,
        'data': data,
    }
    return render(request, 'attendance/daily_attendance_dashboard.html', context)















from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from attendance.models import WorkPlanTitle
from .forms import WorkPlanTitleForm

def is_superuser(user):
    return user.is_superuser

# ---------------------------
# WorkPlanTitle CRUD (Admin only)
# ---------------------------

@user_passes_test(is_superuser)
def workplantitle_list(request):
    titles = WorkPlanTitle.objects.all().order_by('title')
    return render(request, 'workplan/workplantitle_list.html', {'titles': titles})

@user_passes_test(is_superuser)
def workplantitle_create(request):
    if request.method == 'POST':
        form = WorkPlanTitleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "WorkPlan Title created successfully!")
            return redirect('workplantitle_list')
    else:
        form = WorkPlanTitleForm()
    return render(request, 'workplan/workplantitle_create.html', {'form': form})

@user_passes_test(is_superuser)
def workplantitle_edit(request, pk):
    title = get_object_or_404(WorkPlanTitle, pk=pk)
    if request.method == 'POST':
        form = WorkPlanTitleForm(request.POST, instance=title)
        if form.is_valid():
            form.save()
            messages.success(request, "WorkPlan Title updated successfully!")
            return redirect('workplantitle_list')
    else:
        form = WorkPlanTitleForm(instance=title)
    return render(request, 'workplan/workplantitle_edit.html', {'form': form, 'title': title})

@user_passes_test(is_superuser)
def workplantitle_delete(request, pk):
    title = get_object_or_404(WorkPlanTitle, pk=pk)
    title.delete()
    messages.success(request, "WorkPlan Title deleted successfully!")
    return redirect('workplantitle_list')






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from attendance.models import WorkPlan
from .forms import WorkPlanForm

def is_superuser(user):
    return user.is_superuser

# ---------------------------
# ADMIN CRUD
# ---------------------------

@user_passes_test(is_superuser)
def admin_workplan_list(request):
    workplans = WorkPlan.objects.filter(type='admin_created').order_by('-date')
    return render(request, 'workplan/admin_workplan_list.html', {'workplans': workplans})

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import WorkPlanForm

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def admin_workplan_create(request):
    if request.method == 'POST':
        form = WorkPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.type = 'admin_created'
            plan.save()
            form.save_m2m()
            messages.success(request, "✅ Admin work plan created successfully!")
            return redirect('admin_workplan_list')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = WorkPlanForm()

    return render(request, 'workplan/admin_workplan_create.html', {'form': form})


@user_passes_test(is_superuser)
def admin_workplan_edit(request, pk):
    plan = get_object_or_404(WorkPlan, pk=pk, type='admin_created')
    form = WorkPlanForm(request.POST or None, instance=plan)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Work plan updated successfully!")
        return redirect('admin_workplan_list')
    return render(request, 'workplan/admin_workplan_edit.html', {'form': form, 'plan': plan})

@user_passes_test(is_superuser)
def admin_workplan_delete(request, pk):
    plan = get_object_or_404(WorkPlan, pk=pk, type='admin_created')
    plan.delete()
    messages.success(request, "Work plan deleted successfully!")
    return redirect('admin_workplan_list')


# ---------------------------
# USER CRUD
# ---------------------------

@login_required
def user_workplan_list(request):
    workplans = WorkPlan.objects.filter(created_by=request.user, type='user_created').order_by('-date')
    return render(request, 'workplan/user_workplan_list.html', {'workplans': workplans})

@login_required
def user_workplan_create(request):
    if request.method == 'POST':
        form = WorkPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.type = 'user_created'
            plan.save()
            form.save_m2m()
            messages.success(request, "Work plan created successfully!")
            return redirect('user_workplan_list')
    else:
        form = WorkPlanForm()
    return render(request, 'workplan/user_workplan_create.html', {'form': form})

@login_required
def user_workplan_edit(request, pk):
    plan = get_object_or_404(WorkPlan, pk=pk, created_by=request.user)
    form = WorkPlanForm(request.POST or None, instance=plan)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Work plan updated successfully!")
        return redirect('user_workplan_list')
    return render(request, 'workplan/user_workplan_edit.html', {'form': form, 'plan': plan})

@login_required
def user_workplan_delete(request, pk):
    plan = get_object_or_404(WorkPlan, pk=pk, created_by=request.user)
    plan.delete()
    messages.success(request, "Work plan deleted successfully!")
    return redirect('user_workplan_list')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def workplan_dashboard(request):
    """
    Work Plan Dashboard view.
    Shows buttons for Admin and User work plans.
    """
    return render(request, 'workplan/workplan_dashboard.html')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from attendance.models import WorkType, WorkTypeOption, HourlyReport, WorkDetail
from .forms import WorkTypeForm, WorkTypeOptionForm, HourlyReportForm, WorkDetailForm

# 🧩 WorkType CRUD
@login_required
def worktype_list(request):
    worktypes = WorkType.objects.all()
    return render(request, 'hourly_report/worktype_list.html', {'worktypes': worktypes})

@login_required
def worktype_create(request):
    if request.method == 'POST':
        form = WorkTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Work Type created successfully.")
            return redirect('worktype_list')
    else:
        form = WorkTypeForm()
    return render(request, 'hourly_report/worktype_form.html', {'form': form, 'title': 'Create Work Type'})

@login_required
def worktype_edit(request, pk):
    worktype = get_object_or_404(WorkType, pk=pk)
    form = WorkTypeForm(request.POST or None, instance=worktype)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Work Type updated successfully.")
        return redirect('worktype_list')
    return render(request, 'hourly_report/worktype_form.html', {'form': form, 'title': 'Edit Work Type'})

@login_required
def worktype_delete(request, pk):
    worktype = get_object_or_404(WorkType, pk=pk)
    worktype.delete()
    messages.success(request, "Work Type deleted successfully.")
    return redirect('worktype_list')


# 🧩 HourlyReport CRUD
@login_required
def hourlyreport_list(request):
    reports = HourlyReport.objects.filter(user=request.user).order_by('-report_date', '-report_hour')
    return render(request, 'hourly_report/hourlyreport_list.html', {'reports': reports})

@login_required
def hourlyreport_create(request):
    if request.method == 'POST':
        form = HourlyReportForm(request.POST)
        if form.is_valid():
            hourly = form.save(commit=False)
            hourly.user = request.user
            hourly.save()
            form.save_m2m()
            messages.success(request, "Hourly Report created successfully.")
            return redirect('hourlyreport_list')
    else:
        form = HourlyReportForm()
    return render(request, 'hourly_report/hourlyreport_form.html', {'form': form, 'title': 'Create Hourly Report'})

@login_required
def hourlyreport_edit(request, pk):
    report = get_object_or_404(HourlyReport, pk=pk, user=request.user)
    form = HourlyReportForm(request.POST or None, instance=report)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Hourly Report updated successfully.")
        return redirect('hourlyreport_list')
    return render(request, 'hourly_report/hourlyreport_form.html', {'form': form, 'title': 'Edit Hourly Report'})


# 🧩 WorkDetail CRUD
@login_required
def workdetail_list(request):
    details = WorkDetail.objects.select_related('hourly_report', 'work_type_option', 'project')
    return render(request, 'hourly_report/workdetail_list.html', {'details': details})

@login_required
def workdetail_create(request):
    if request.method == 'POST':
        form = WorkDetailForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Work Detail added successfully.")
            return redirect('workdetail_list')
    else:
        form = WorkDetailForm()
    return render(request, 'hourly_report/workdetail_form.html', {'form': form, 'title': 'Add Work Detail'})

@login_required
def workdetail_edit(request, pk):
    detail = get_object_or_404(WorkDetail, pk=pk)
    form = WorkDetailForm(request.POST or None, instance=detail)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Work Detail updated successfully.")
        return redirect('workdetail_list')
    return render(request, 'hourly_report/workdetail_form.html', {'form': form, 'title': 'Edit Work Detail'})


from django.shortcuts import render
from django.contrib.auth.models import User
from attendance.models import HourlyReport



def report_dashboard(request):
    users = User.objects.all()
    selected_user = request.GET.get('user')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    reports = HourlyReport.objects.all().select_related('user').prefetch_related('work_types', 'work_type_options', 'details')

    if selected_user:
        reports = reports.filter(user_id=selected_user)
    if from_date:
        reports = reports.filter(report_date__gte=from_date)
    if to_date:
        reports = reports.filter(report_date__lte=to_date)

    context = {
        'reports': reports,
        'users': users,
        'selected_user': selected_user,
        'from_date': from_date,
        'to_date': to_date,
        'total_reports': reports.count(),
        'work_done_count': reports.filter(work_done='yes').count(),
        'work_not_done_count': reports.filter(work_done='no').count(),
    }
    return render(request, 'hourly_report/report_dashboard.html', context)



from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Sum
from datetime import date
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import MonthlyTarget, Sale
from .serializers import MonthlyTargetSerializer, SaleSerializer
from .permissions import IsSuperUser


class MonthlyTargetViewSet(viewsets.ModelViewSet):
    queryset = MonthlyTarget.objects.all()
    serializer_class = MonthlyTargetSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def perform_create(self, serializer):
        serializer.save()


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def perform_create(self, serializer):
        serializer.save()


class UserTargetStatusViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def list(self, request):
        """Show target/sale summary for all users."""
        year = date.today().year
        users = User.objects.all().order_by('id')
        response_data = []

        for user in users:
            targets = MonthlyTarget.objects.filter(user=user, year=year).order_by('month')
            if not targets.exists():
                continue  # skip users with no targets

            monthly_status = []
            carry_forward = 0

            for target in targets:
                sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
                total_sold = sales['total_sold'] or 0
                effective_sold = total_sold + carry_forward

                if effective_sold >= target.target_area:
                    status_color = 'green'
                    carry_forward = effective_sold - target.target_area
                else:
                    status_color = 'red'
                    carry_forward = 0

                monthly_status.append({
                    'month': target.get_month_display(),
                    'target_area': target.target_area,
                    'sold_area': total_sold,
                    'status': status_color,
                    'carry_forward': carry_forward,
                })

            response_data.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'year': year,
                'monthly_status': monthly_status
            })

        return Response(response_data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Show target/sale summary for one user."""
        user = get_object_or_404(User, id=pk)
        year = date.today().year
        targets = MonthlyTarget.objects.filter(user=user, year=year).order_by('month')

        if not targets.exists():
            return Response({"detail": "No targets found for this user."}, status=status.HTTP_404_NOT_FOUND)

        monthly_status = []
        carry_forward = 0

        for target in targets:
            sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
            total_sold = sales['total_sold'] or 0
            effective_sold = total_sold + carry_forward

            if effective_sold >= target.target_area:
                status_color = 'green'
                carry_forward = effective_sold - target.target_area
            else:
                status_color = 'red'
                carry_forward = 0

            monthly_status.append({
                'month': target.get_month_display(),
                'target_area': target.target_area,
                'sold_area': total_sold,
                'status': status_color,
                'carry_forward': carry_forward,
            })

        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'year': year,
            'monthly_status': monthly_status
        }, status=status.HTTP_200_OK)


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Sum
from datetime import date
from django.contrib.auth.models import User

from .models import MonthlyTarget, Sale
from .permissions import IsSuperUser


class TargetAndSaleDashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for showing target and sale dashboard summary.
    Only accessible by superusers.
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def list(self, request):
        today = date.today()

        # Optional year/month filtering from query params
        year = int(request.query_params.get('year', today.year))
        month = request.query_params.get('month')
        if month:
            month = int(month)

        total_targets = MonthlyTarget.objects.filter(year=year)
        total_sales = Sale.objects.filter(year=year)
        total_users = User.objects.exclude(is_superuser=True).count()

        total_target_area = total_targets.aggregate(total=Sum('target_area'))['total'] or 0
        total_sold_area = total_sales.aggregate(total=Sum('area_sold'))['total'] or 0

        progress_percent = round((total_sold_area / total_target_area) * 100, 2) if total_target_area else 0.0

        users_status = []
        users = User.objects.exclude(is_superuser=True).order_by('username')

        for user in users:
            user_targets = MonthlyTarget.objects.filter(user=user, year=year)
            if month:
                user_targets = user_targets.filter(month=month)
            user_targets = user_targets.order_by('month')

            monthly_status = []
            carry_forward = 0

            for target in user_targets:
                sales = Sale.objects.filter(user=user, year=year, month=target.month).aggregate(total_sold=Sum('area_sold'))
                total_sold = sales['total_sold'] or 0
                effective_sold = total_sold + carry_forward

                if effective_sold >= target.target_area:
                    status_color = 'green'
                    carry_forward = effective_sold - target.target_area
                else:
                    status_color = 'red'
                    carry_forward = 0

                monthly_status.append({
                    'month': target.get_month_display(),
                    'target_area': target.target_area,
                    'sold_area': total_sold,
                    'status': status_color,
                    'carry_forward': carry_forward,
                })

            users_status.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'monthly_status': monthly_status,
            })

        data = {
            'year': year,
            'month': month,
            'total_targets_count': total_targets.count(),
            'total_sales_count': total_sales.count(),
            'total_users_count': total_users,
            'total_target_area': total_target_area,
            'total_sold_area': total_sold_area,
            'progress_percent': progress_percent,
            'users_status': users_status,
        }

        return Response(data, status=status.HTTP_200_OK)



# admin_section/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from attendance.models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from .permissions import IsSuperUser

class AdminUserViewSet(viewsets.ViewSet):
    permission_classes = [IsSuperUser]

    def list(self, request):
        filter_type = request.query_params.get('filter', 'all')

        users = User.objects.all().order_by('-date_joined')
        if filter_type == 'pending':
            users = users.filter(is_active=False, is_superuser=False)
        elif filter_type == 'approved':
            users = users.filter(is_active=True, is_superuser=False)
        elif filter_type == 'admins':
            users = users.filter(is_superuser=True)

        serializer = UserSerializer(users, many=True)
        return Response({
            "summary": {
                "total_users": User.objects.exclude(is_superuser=True).count(),
                "approved_users": User.objects.filter(is_active=True, is_superuser=False).count(),
                "pending_users": User.objects.filter(is_active=False, is_superuser=False).count(),
                "super_users": User.objects.filter(is_superuser=True).count(),
                "active_filter": filter_type,
            },
            "users": serializer.data
        })

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save()
        return Response({"message": f"{user.username} approved successfully."})

    @action(detail=True, methods=['put'])
    def edit(self, request, pk=None):
        """
        ✅ Update user info + profile safely.
        """
        user = get_object_or_404(User, pk=pk)

        # --- Update basic user fields ---
        user.username = request.data.get('username', user.username)
        user.email = request.data.get('email', user.email)
        user.save()

        # --- Handle Profile ---
        profile_data = request.data.get('profile', {})
        profile, created = UserProfile.objects.get_or_create(user=user)

        serializer = UserProfileSerializer(profile, data=profile_data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = UserSerializer(user)
        return Response({
            "message": "User and profile updated successfully.",
            "user": user_serializer.data
        })

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)




from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from datetime import date, timedelta
import calendar
from geopy.geocoders import Nominatim
from attendance.models import Attendance
from .permissions import IsSuperUser


class AttendanceDashboardViewSet(viewsets.ViewSet):
    """
    Superuser-only Attendance Dashboard APIs
    """

    permission_classes = [IsAuthenticated, IsSuperUser]

    # =========================
    # DAILY ATTENDANCE DASHBOARD
    # =========================
    @action(detail=False, methods=['get'])
    def daily(self, request):
        today = date.today()
        users = User.objects.exclude(is_superuser=True).order_by('username')

        total_employees = users.count()
        present_count = 0
        absent_count = 0

        geolocator = Nominatim(user_agent="attendance_app")

        data = []
        for user in users:
            attendance = Attendance.objects.filter(user=user, date=today).first()

            if attendance and attendance.check_in_time:
                status_label = 'Present'
                present_count += 1
            else:
                status_label = 'Absent'
                absent_count += 1

            # Get location names safely
            def get_location(lat, lon):
                if lat and lon:
                    try:
                        location = geolocator.reverse(f"{lat},{lon}", timeout=10)
                        return location.address if location else '-'
                    except:
                        return '-'
                return '-'

            data.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'status': status_label,
                'check_in': attendance.check_in_time.strftime("%H:%M:%S") if attendance and attendance.check_in_time else '-',
                'check_in_location': get_location(attendance.check_in_latitude, attendance.check_in_longitude) if attendance else '-',
                'check_out': attendance.check_out_time.strftime("%H:%M:%S") if attendance and attendance.check_out_time else '-',
                'check_out_location': get_location(attendance.check_out_latitude, attendance.check_out_longitude) if attendance else '-',
            })

        return Response({
            'date': today,
            'total_employees': total_employees,
            'present_count': present_count,
            'absent_count': absent_count,
            'attendance_data': data
        }, status=status.HTTP_200_OK)

    # =========================
    # MONTHLY ATTENDANCE DASHBOARD
    # =========================
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        today = date.today()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        total_days = calendar.monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, total_days)

        users = User.objects.exclude(is_superuser=True).order_by('username')
        attendance_summary = []

        for user in users:
            daily_status = []
            for day in range(1, total_days + 1):
                current_date = date(year, month, day)
                attendance = Attendance.objects.filter(user=user, date=current_date).first()

                if attendance:
                    daily_status.append('P')  # Present
                else:
                    if current_date > today:
                        daily_status.append('-')  # Future
                    else:
                        daily_status.append('A')  # Absent

            attendance_summary.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'attendance_days': daily_status
            })

        return Response({
            'month': month,
            'year': year,
            'days_in_month': list(range(1, total_days + 1)),
            'attendance_summary': attendance_summary
        }, status=status.HTTP_200_OK)


# admin_section/views/workplan_api.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from attendance.models import WorkPlanTitle
from admin_section.serializers import WorkPlanTitleSerializer
from admin_section.permissions import IsSuperUser


class WorkPlanTitleViewSet(viewsets.ModelViewSet):
    """
    Superuser-only CRUD for WorkPlan Titles
    """
    queryset = WorkPlanTitle.objects.all().order_by('title')
    serializer_class = WorkPlanTitleSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "WorkPlan Title created successfully!", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "WorkPlan Title updated successfully!", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "WorkPlan Title deleted successfully!"}, status=status.HTTP_200_OK)



# admin_section/views/workplan_admin_api.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from attendance.models import WorkPlan
from admin_section.serializers import WorkPlanSerializer
from admin_section.permissions import IsSuperUser


class AdminWorkPlanViewSet(viewsets.ModelViewSet):
    """
    API for Superusers to manage Admin-Created WorkPlans
    """
    serializer_class = WorkPlanSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]

    def get_queryset(self):
        return WorkPlan.objects.filter(type='admin_created').order_by('-date')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, type='admin_created')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "✅ Admin work plan created successfully!", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Work plan updated successfully!", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Work plan deleted successfully!"}, status=status.HTTP_200_OK)


# admin_section/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from attendance.models import WorkPlan
from .serializers import WorkPlanSerializer

class UserWorkPlanViewSet(viewsets.ModelViewSet):
    serializer_class = WorkPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the logged-in user's workplans."""
        return WorkPlan.objects.filter(created_by=self.request.user, type='user_created').order_by('-date')

    def perform_create(self, serializer):
        """Automatically assign created_by and type."""
        serializer.save(created_by=self.request.user, type='user_created')

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """Get all workplans for a specific month and year."""
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not month or not year:
            return Response({'error': 'Please provide month and year in query parameters.'}, status=status.HTTP_400_BAD_REQUEST)

        workplans = WorkPlan.objects.filter(
            created_by=request.user,
            type='user_created',
            date__year=year,
            date__month=month
        ).order_by('-date')

        serializer = self.get_serializer(workplans, many=True)
        return Response(serializer.data)


from rest_framework import viewsets, permissions
from attendance.models import WorkType, WorkTypeOption, HourlyReport, WorkDetail
from .serializers import (
    WorkTypeSerializer, WorkTypeOptionSerializer,
    HourlyReportSerializer, WorkDetailSerializer
)


# 🧩 WorkType CRUD
class WorkTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkType.objects.all()
    serializer_class = WorkTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# 🧩 WorkTypeOption CRUD
class WorkTypeOptionViewSet(viewsets.ModelViewSet):
    queryset = WorkTypeOption.objects.all()
    serializer_class = WorkTypeOptionSerializer
    permission_classes = [permissions.IsAuthenticated]


# 🧩 HourlyReport CRUD
class HourlyReportViewSet(viewsets.ModelViewSet):
    serializer_class = HourlyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Each user can only access their own reports
        return HourlyReport.objects.filter(user=self.request.user).order_by('-report_date', '-report_hour')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 🧩 WorkDetail CRUD
class WorkDetailViewSet(viewsets.ModelViewSet):
    serializer_class = WorkDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkDetail.objects.select_related('hourly_report', 'work_type_option', 'project')





from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from attendance.models import (
    Attendance, WorkPlan, WorkType, WorkTypeOption,
    HourlyReport, WorkDetail
)
from datetime import date
from .permissions import IsSuperUser
from django.db import models

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from attendance.models import (
    Attendance, WorkPlan, WorkType, WorkTypeOption,
    HourlyReport, WorkDetail, Project
)
from datetime import date
from .permissions import IsSuperUser
from django.db import models

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import models
from datetime import date
from .permissions import IsSuperUser



class DashboardViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def list(self, request):
        today = date.today()

        # ----------------------
        # USER & ATTENDANCE DATA
        # ----------------------
        users = User.objects.exclude(is_superuser=True)
        total_users = users.count()

        checked_in_att = Attendance.objects.filter(date=today, check_in_time__isnull=False)
        checked_out_att = Attendance.objects.filter(date=today, check_out_time__isnull=False)

        checked_in_count = checked_in_att.count()
        not_checked_in_count = total_users - checked_in_count

        # Helper to get full name
        def get_user_name(user):
            try:
                full = f"{user.profile.first_name} {user.profile.last_name}".strip()
                return full or user.username
            except:
                return user.username

        # ----------------------
        # RECENT ACTIVITY
        # ----------------------
        recent_activity = []

        # 1️⃣ User Signups today
        for u in users.filter(date_joined__date=today):
            recent_activity.append({
                "title": "User Signed Up",
                "description": f"{get_user_name(u)} signed up",
                "time": u.date_joined.strftime('%H:%M'),
                "user_id": u.id,
                "icon": "fa-user-plus",
                "color": "var(--info)"
            })

        # 2️⃣ User Logins today
        for u in users.filter(last_login__date=today):
            recent_activity.append({
                "title": "User Logged In",
                "description": f"{get_user_name(u)} logged in",
                "time": u.last_login.strftime('%H:%M'),
                "user_id": u.id,
                "icon": "fa-sign-in-alt",
                "color": "var(--success)"
            })

        # 3️⃣ Attendance check-in
        for att in checked_in_att:
            recent_activity.append({
                "title": "Checked In",
                "description": f"{get_user_name(att.user)} checked in at {att.check_in_time.strftime('%I:%M %p')}",
                "time": att.check_in_time.strftime('%H:%M'),
                "user_id": att.user.id,
                "icon": "fa-sign-in-alt",
                "color": "var(--success)"
            })

        # 4️⃣ Attendance check-out (also treat as logout)
        for att in checked_out_att:
            recent_activity.append({
                "title": "Checked Out / Logged Out",
                "description": f"{get_user_name(att.user)} checked out at {att.check_out_time.strftime('%I:%M %p')}",
                "time": att.check_out_time.strftime('%H:%M'),
                "user_id": att.user.id,
                "icon": "fa-sign-out-alt",
                "color": "var(--warning)"
            })

        # 5️⃣ Profile created / updated today
        for p in UserProfile.objects.filter(created_at__date=today):
            recent_activity.append({
                "title": "Profile Created",
                "description": f"{get_user_name(p.user)} created profile",
                "time": p.created_at.strftime('%H:%M'),
                "user_id": p.user.id,
                "icon": "fa-id-card",
                "color": "var(--info)"
            })

        for p in UserProfile.objects.filter(updated_at__date=today):
            recent_activity.append({
                "title": "Profile Updated",
                "description": f"{get_user_name(p.user)} updated profile",
                "time": p.updated_at.strftime('%H:%M'),
                "user_id": p.user.id,
                "icon": "fa-edit",
                "color": "var(--warning)"
            })

        # 6️⃣ Project created today
        for proj in Project.objects.filter(created_at__date=today):
            recent_activity.append({
                "title": "Project Created",
                "description": f"{proj.name} project created",
                "time": proj.created_at.strftime('%H:%M'),
                "user_id": proj.created_by.id if proj.created_by else None,
                "icon": "fa-building",
                "color": "var(--dark)"
            })

        # 7️⃣ Monthly Target created today
        for mt in MonthlyTarget.objects.filter(user__in=users, month=today.month, year=today.year):
            recent_activity.append({
                "title": "Monthly Target Set",
                "description": f"{get_user_name(mt.user)} set monthly target",
                "time": "09:00",
                "user_id": mt.user.id,
                "icon": "fa-bullseye",
                "color": "var(--primary)"
            })

        # 8️⃣ Sale added today
        for sale in Sale.objects.filter(user__in=users, month=today.month, year=today.year):
            recent_activity.append({
                "title": "Sale Added",
                "description": f"{get_user_name(sale.user)} added sale {sale.area_sold} sq ft",
                "time": "09:30",
                "user_id": sale.user.id,
                "icon": "fa-chart-line",
                "color": "var(--success)"
            })

        # 9️⃣ WorkPlan created today
        for wp in WorkPlan.objects.filter(created_at__date=today):
            recent_activity.append({
                "title": "Work Plan Created",
                "description": f"{get_user_name(wp.created_by)} created a work plan",
                "time": wp.created_at.strftime('%H:%M'),
                "user_id": wp.created_by.id,
                "icon": "fa-tasks",
                "color": "var(--primary)"
            })

        # 🔟 HourlyReport submitted today
        for hr in HourlyReport.objects.filter(created_at__date=today):
            recent_activity.append({
                "title": "Hourly Report",
                "description": f"{get_user_name(hr.user)} submitted hourly report ({hr.report_hour}:00)",
                "time": hr.created_at.strftime('%H:%M'),
                "user_id": hr.user.id,
                "icon": "fa-clock",
                "color": "var(--info)"
            })

        # Sort all activities by time descending
        recent_activity = sorted(recent_activity, key=lambda x: x['time'], reverse=True)

        # ----------------------
        # WORKPLAN SUMMARY
        # ----------------------
        workplans_today = WorkPlan.objects.filter(date=today)
        total_workplans = workplans_today.count()
        completed_workplans = workplans_today.filter(status='completed').count()
        pending_workplans = total_workplans - completed_workplans

        admin_workplans_count = WorkPlan.objects.filter(type='admin_created').count()
        user_workplans_count = WorkPlan.objects.filter(type='user_created').count()

        # ----------------------
        # WORKTYPE & OPTION DATA
        # ----------------------
        worktype_count = WorkType.objects.count()
        worktype_option_count = WorkTypeOption.objects.count()

        # ----------------------
        # HOURLY REPORT DATA
        # ----------------------
        hourly_total = HourlyReport.objects.count()
        hourly_today = HourlyReport.objects.filter(report_date=today).count()
        hourly_work_done = HourlyReport.objects.filter(work_done="yes").count()
        hourly_work_not_done = HourlyReport.objects.filter(work_done="no").count()

        # ----------------------
        # WORK DETAIL DATA
        # ----------------------
        workdetail_total = WorkDetail.objects.count()
        customer_response = {
            "interested": WorkDetail.objects.filter(customer_response='interested').count(),
            "not_interested": WorkDetail.objects.filter(customer_response='not_interested').count(),
            "not_sure": WorkDetail.objects.filter(customer_response='not_sure').count(),
        }
        project_details = (
            WorkDetail.objects.values('project__name')
            .order_by('project__name')
            .annotate(total=models.Count('id'))
        )

        # ----------------------
        # FINAL RESPONSE
        # ----------------------
        return Response({
            "total_users": total_users,
            "checked_in_count": checked_in_count,
            "not_checked_in_count": not_checked_in_count,
            "recent_activity": recent_activity,

            "total_workplans": total_workplans,
            "completed_workplans": completed_workplans,
            "pending_workplans": pending_workplans,
            "admin_workplans_count": admin_workplans_count,
            "user_workplans_count": user_workplans_count,

            "worktype_count": worktype_count,
            "worktype_option_count": worktype_option_count,

            "hourly_report_total": hourly_total,
            "hourly_report_today": hourly_today,
            "hourly_work_done": hourly_work_done,
            "hourly_work_not_done": hourly_work_not_done,

            "workdetail_total": workdetail_total,
            "customer_response": customer_response,
            "project_wise_work_details": list(project_details),
        })
