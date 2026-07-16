from django import forms
from shopapp.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "price", "description", "preview")

class OrderImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV file with orders')