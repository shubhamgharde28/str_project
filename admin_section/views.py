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

