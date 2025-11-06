from django import forms
from .models import MonthlyTarget, Sale

from django import forms
from .models import MonthlyTarget, Sale
from datetime import date

class MonthlyTargetForm(forms.ModelForm):
    class Meta:
        model = MonthlyTarget
        fields = ['user', 'month', 'year', 'target_area']

    def __init__(self, *args, **kwargs):
        super(MonthlyTargetForm, self).__init__(*args, **kwargs)
        # Generate a list of years: current year ± 5
        current_year = date.today().year
        year_choices = [(y, y) for y in range(current_year - 5, current_year + 6)]
        self.fields['year'] = forms.ChoiceField(choices=year_choices)


from django import forms
from .models import Sale
from datetime import date

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['user', 'month', 'year', 'area_sold']

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        # Year dropdown: current year ± 5
        current_year = date.today().year
        year_choices = [(y, y) for y in range(current_year - 5, current_year + 6)]
        self.fields['year'] = forms.ChoiceField(choices=year_choices)





from django import forms
from attendance.models import WorkPlanTitle

class WorkPlanTitleForm(forms.ModelForm):
    class Meta:
        model = WorkPlanTitle
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }

from django import forms
from django.contrib.auth.models import User
from attendance.models import WorkPlan, WorkPlanTitle

from django import forms
from django.contrib.auth.models import User
from attendance.models import WorkPlan, WorkPlanTitle


class WorkPlanForm(forms.ModelForm):
    coworkers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_superuser=False),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    titles = forms.ModelMultipleChoiceField(
        queryset=WorkPlanTitle.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    class Meta:
        model = WorkPlan
        fields = ['titles', 'description', 'coworkers', 'status', 'date']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter work plan details...'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

from django import forms
from attendance.models import WorkType, WorkTypeOption, HourlyReport, WorkDetail

class WorkTypeForm(forms.ModelForm):
    class Meta:
        model = WorkType
        fields = ['name', 'description']

class WorkTypeOptionForm(forms.ModelForm):
    class Meta:
        model = WorkTypeOption
        fields = ['work_type', 'name', 'description']

class HourlyReportForm(forms.ModelForm):
    class Meta:
        model = HourlyReport
        fields = [
            'report_date', 'report_hour', 'location_latitude', 'location_longitude',
            'work_done', 'reason_not_done', 'work_types', 'work_type_options'
        ]
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            'reason_not_done': forms.Textarea(attrs={'rows': 2}),
            'work_types': forms.CheckboxSelectMultiple(),
            'work_type_options': forms.CheckboxSelectMultiple(),
        }

class WorkDetailForm(forms.ModelForm):
    class Meta:
        model = WorkDetail
        fields = [
            'hourly_report', 'project', 'work_type_option', 'customer_name',
            'mobile_number', 'plot_number', 'customer_response', 'reason_not_interested',
            'site_visit_done', 'meeting_done', 'booking_done', 'next_followup_date'
        ]
        widgets = {
            'next_followup_date': forms.DateInput(attrs={'type': 'date'}),
            'reason_not_interested': forms.Textarea(attrs={'rows': 2}),
        }
