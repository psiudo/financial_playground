# insight/forms.py

from django import forms
from .models import InterestStock


class InterestStockForm(forms.ModelForm):
    class Meta:
        model = InterestStock
        fields = ['company_name']
        labels = {
            'company_name': '관심 종목명'
        }
