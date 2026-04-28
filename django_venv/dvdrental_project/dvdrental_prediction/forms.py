from django import forms
from .models import Actor, Category, Language

# 1. Form Pencarian (Lama - Supaya View Search tidak Error)
class MovieSearchForm(forms.Form):
    actor = forms.ModelChoiceField(queryset=Actor.objects.all(), required=False, empty_label="Select Actor")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="Select Category")
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False, empty_label="Select Language")

# 2. Form Prediksi ML (Baru)
class MovieDemandForm(forms.Form):
    rental_duration = forms.IntegerField(
        label='Rental Duration (Hari)',
        min_value=0, 
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    rental_rate = forms.DecimalField(
        label='Rental Rate ($)',
        min_value=0, 
        max_digits=4, decimal_places=2, initial=2.99,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    length = forms.IntegerField(
        label='Length (Menit)',
        min_value=0, 
        initial=120,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    replacement_cost = forms.DecimalField(
        label='Replacement Cost ($)', 
        min_value=0,
        max_digits=5, decimal_places=2, initial=19.99,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

# 3. Form Prediksi Customer Value (Baru)
class CustomerPredictionForm(forms.Form):
    store_id = forms.IntegerField(label='Store ID', min_value=1)
    active = forms.IntegerField(label='Active (0 or 1)', min_value=0, max_value=1)
    total_payment = forms.FloatField(label='Total Payment', min_value=0)
    payment_count = forms.IntegerField(label='Payment Count', min_value=0)
    average_payment = forms.FloatField(label='Average Payment', min_value=0)