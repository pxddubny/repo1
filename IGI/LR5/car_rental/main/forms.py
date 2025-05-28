from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re

class UserRegisterForm(UserCreationForm):
    phone = forms.CharField(
        label='phone',
        help_text='format: +375 (29) XXX-XX-XX',
        widget=forms.TextInput(attrs={'placeholder': '+375 (29) XXX-XX-XX'})
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'middle_name',
            'email', 'birth_date', 'phone', 'address', 'password1', 'password2'
        ]

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(r'^\+375\s\(\d{2}\)\s\d{3}-\d{2}-\d{2}$', phone):
            raise forms.ValidationError("not right format!")
        return phone