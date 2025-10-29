from django import forms
from .models import Order
from .models import ShippingOption


class ShippingForm(forms.Form):
    shipping_option = forms.ModelChoiceField(
        queryset=ShippingOption.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None
    )

from .models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        widgets = {
            'value': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)])
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'address', 'city', 'postal_code', 'phone', 'shipping_option']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'small-input'}),
            'address': forms.TextInput(attrs={'class': 'small-input'}),
            'city': forms.TextInput(attrs={'class': 'small-input'}),
            'postal_code': forms.TextInput(attrs={'class': 'small-input'}),
            'phone': forms.TextInput(attrs={'class': 'small-input'}),
            'shipping_option': forms.RadioSelect(),
        }

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    phone = forms.CharField(max_length=20)
    shipping_option = forms.ModelChoiceField(queryset=ShippingOption.objects.all())


