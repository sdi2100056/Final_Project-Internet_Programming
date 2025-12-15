from django import forms
from django.contrib.auth.forms import UserCreationForm #Django's built-in user registration form
from django.contrib.auth.models import User#Django's built-ion user model
from .models import UserProfile, Product, Category

#Extends django's user registration form
class UserRegisterForm(UserCreationForm):
    #Add additional required fieldsto the User Creation Form
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
#Defines which model and fields this form is associated with
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

#User profile form
class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
#Meta class fo User Profile model configuration
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'postal_code', 'date_of_birth']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
#Custom initialization to pre populate User model fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

#Product filter form for filtering products on the product list page
class ProductFilterForm(forms.Form):
    #Search Field for text filtering
    search = forms.CharField(max_length=200, required=False)
    #Category filter
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="All")
    #Price range filter
    min_price = forms.DecimalField(required=False)
    max_price = forms.DecimalField(required=False)
    #Size filter
    size = forms.ChoiceField(choices=[('', 'All')] + list(Product.SIZE_CHOICES), required=False)
    type = forms.ChoiceField(choices=[('', 'All')] + list(Product.TYPE_CHOICES), required=False)
    season = forms.ChoiceField(choices=[('', 'All')] + list(Product.SEASON_CHOICES), required=False)
