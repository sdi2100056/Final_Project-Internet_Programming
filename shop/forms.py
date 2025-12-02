from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Product, Category


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'postal_code', 'date_of_birth']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email


class ProductFilterForm(forms.Form):
    search = forms.CharField(max_length=200, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="Όλες")
    min_price = forms.DecimalField(required=False)
    max_price = forms.DecimalField(required=False)
    size = forms.ChoiceField(choices=[('', 'Όλα')] + list(Product.SIZE_CHOICES), required=False)
    type = forms.ChoiceField(choices=[('', 'Όλοι')] + list(Product.TYPE_CHOICES), required=False)
    season = forms.ChoiceField(choices=[('', 'Όλες')] + list(Product.SEASON_CHOICES), required=False)
