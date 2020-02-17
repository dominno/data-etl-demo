from django import forms

from metrics.models import Datasource, Campaign


class MetricFilterForm(forms.Form):
    datasources = forms.ModelMultipleChoiceField(queryset=Datasource.objects.all(), required=False)
    campaigns = forms.ModelMultipleChoiceField(queryset=Campaign.objects.all(), required=False)
    start_date = forms.DateField(required=False, help_text="Date format: YYYY-MM-DD")
    end_date = forms.DateField(required=False, help_text="Date format: YYYY-MM-DD")
