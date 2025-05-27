# simulator/forms.py
from django import forms

class BuyForm(forms.Form):
    stock_name = forms.CharField(label='종목명', max_length=100)
    quantity = forms.IntegerField(label='수량', min_value=1)
    price = forms.IntegerField(label='매수가격', min_value=1)
