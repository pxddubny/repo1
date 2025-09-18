from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re
from django.utils import timezone
from .models import Car, PromoCode

from django import forms
from django.utils import timezone
from .models import Rental, Car, PromoCode
from datetime import datetime


class RentalForm(forms.ModelForm):
    promo_code_input = forms.CharField(
        max_length=50,
        required=False,
        label="Промокод (если есть)",
        help_text="Введите код промокода",
        widget=forms.TextInput(attrs={'placeholder': 'ABCD123'})
    )

    class Meta:
        model = Rental
        fields = ['car', 'days', 'start_date']  # Убрали promo_code из fields
        labels = {
            'car': "Автомобиль",
            'days': "Количество дней",
            'start_date': "Дата начала",
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_promo_code_input(self):
        """Валидация промокода"""
        code = self.cleaned_data.get('promo_code_input', '').strip()
        if not code:
            return None
            
        try:
            promo = PromoCode.objects.get(
                code__iexact=code,
                is_active=True
            )
            return promo
        except PromoCode.DoesNotExist:
            raise forms.ValidationError("Неверный или неактивный промокод")

    def save(self, commit=True):
        """Сохранение с применением промокода"""
        instance = super().save(commit=False)
        promo = self.cleaned_data.get('promo_code_input')
        
        if promo:
            instance.promo_code = promo
            # Пересчет суммы с учетом скидки
            instance.discount_amount = (instance.rental_amount * promo.discount) / 100
            instance.total_amount = instance.rental_amount - instance.discount_amount
        
        if commit:
            instance.save()
            self.save_m2m()
            
        return instance
class UserRegisterForm(UserCreationForm):
    phone = forms.CharField(
        label='Phone',
        help_text='Format: +375 (29) XXX-XX-XX',
        widget=forms.TextInput(attrs={
            'placeholder': '+375 (29) XXX-XX-XX',
            'pattern': '\+375\s\(\d{2}\)\s\d{3}-\d{2}-\d{2}',
            'title': 'Format: +375 (29) XXX-XX-XX'
        })
    )
    birth_date = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Your address'})
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
            raise forms.ValidationError("Phone format: +375 (29) XXX-XX-XX")
        return phone