from django import forms
from django_countries.fields import CountryField
from .models import Address


# class CheckoutForm(forms.Form):
# 	shipping_address1 = forms.CharField(label="Address", max_length=100)
# 	shipping_address2 = forms.CharField(label="Address 2 (optional)", max_length=100)
# 	shipping_country = CountryField(blank_label='(select country)').formfield(
#         required=False,
#         widget=CountrySelectWidget(attrs={
#             'class': 'custom-select d-block w-100',
#         }))
# 	shipping_zip = forms.CharField(label="Zip", max_length=32)

# 	shipping_address1 = forms.CharField(label="Address", max_length=100)
# 	shipping_address2 = forms.CharField(label="Address 2 (optional)", max_length=100)
# 	shipping_country = CountryField(blank_label='(select country)').formfield(
#         required=False,
#         widget=CountrySelectWidget(attrs={
#             'class': 'custom-select d-block w-100',
#         }))
# 	shipping_zip = forms.CharField(label="Zip", max_length=32)

# 	same_billing_address = forms.BooleanField(required=False)


# class Address(forms.ModelForm):
# 	


# class SearchForm(forms.Form):
# 	q = form.CharField(max_length=32)
