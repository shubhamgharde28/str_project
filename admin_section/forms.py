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


