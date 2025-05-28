from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from django.conf import settings
import datetime
from decimal import Decimal

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    img_path = models.CharField(max_length=255, blank=True, default='')  # Пустая строка по умолчанию
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'

class FAQ(models.Model):
    title = models.CharField('title',max_length=200)
    question = models.TextField('question')
    answer = models.TextField('answer')
    ans_date = models.DateTimeField('date',auto_now_add=True)

    def __str__(self):
        return self.title

class ContactInfo(models.Model):
    title = models.CharField('title',max_length=200)
    question = models.TextField('question')
    answer = models.TextField('answer')
    ans_date = models.DateTimeField('date',auto_now_add=True)

    def __str__(self):
        return self.title

class Employee(models.Model):
    name = models.CharField('name', max_length=100)
    position = models.CharField('position', max_length=200)
    description = models.TextField('description')
    phone = models.CharField('phone', max_length=20)
    email = models.EmailField('email')
    photo_path = models.CharField(max_length=255, blank=True, default='')
    
    def __str__(self):
        return f"{self.name} - {self.position}"

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

class Vacancy(models.Model):
    title = models.CharField('title', max_length=200)
    description = models.TextField('description')
    requirements = models.TextField('requirements')
    salary = models.CharField('salary', max_length=100, blank=True)
    is_active = models.BooleanField('active', default=True)
    created_at = models.DateTimeField('date', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Vacancy'
        verbose_name_plural = 'Vacancies'

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField('name', max_length=100)
    rating = models.PositiveSmallIntegerField('rating', choices=RATING_CHOICES)
    text = models.TextField('text')
    created_at = models.DateTimeField('date', auto_now_add=True)
    is_published = models.BooleanField('published', default=False)

    def __str__(self):
        return f"Review by {self.name} ({self.rating}/5)"

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

class PromoCode(models.Model):
    code = models.CharField('code', max_length=50, unique=True)
    description = models.TextField('description')
    discount = models.PositiveSmallIntegerField('discount')
    is_active = models.BooleanField('active', default=True)  # Добавьте это поле

    def __str__(self):
        return f"{self.code} ({self.discount}%)"

    class Meta:
        verbose_name = 'Promo Code'
        verbose_name_plural = 'Promo Codes'


class Fine(models.Model):
    name = models.CharField('name')
    fine = models.DecimalField('fine',max_digits=8, decimal_places=2,)

    def __str__(self):
        return f"{self.name} ({self.fine})"

    class Meta:
        verbose_name = 'Fine'
        verbose_name_plural = 'Fines'
        
# 1. Тип кузова (OneToOne пример)
class BodyType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# 2. Модели авто (ForeignKey пример)
class CarModel(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

# 3. Автомобили (основная модель)
class Car(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    body_type = models.OneToOneField(BodyType, on_delete=models.PROTECT,  null=True, blank=True)  # Пример OneToOne
    year = models.PositiveIntegerField()
    daily_rental_price = models.DecimalField(max_digits=8, decimal_places=2, editable = False)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.model} ({self.license_plate})"

    def save(self, *args, **kwargs):
        current_year = timezone.now().year
        age = current_year - self.year

        self.daily_rental_price = (float(str(self.price)) * max(0.5, 1 - (age * 0.05)) *0.01) 
        super().save(*args, **kwargs)

#rega

def validate_phone(value):
    """Валидация номера в формате +375 (29) XXX-XX-XX"""
    pattern = r'^\+375\s\(\d{2}\)\s\d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Номер должен быть в формате +375 (29) XXX-XX-XX')

def validate_age(value):
    """Проверка что пользователю 18+"""
    if (timezone.now().date() - value).days < 365 * 18:
        raise ValidationError('age must be18+')

class User(AbstractUser):
    ROLES = (
        ('GUEST', 'guest'),
        ('CLIENT', 'client'),
        ('MANAGER', 'manager'),
        ('SUPERUSER', 'superuser')
    )
    middle_name = models.CharField('middle name', max_length=150, blank=True)
    phone = models.CharField('phone', max_length=20, validators=[validate_phone])
    birth_date = models.DateField('bd date', validators=[validate_age], null=True, blank=True)
    address = models.TextField('address')
    role = models.CharField('role', max_length=10, choices=ROLES, default='CLIENT')
    promocodes = models.ManyToManyField(PromoCode, blank=True)
    fines = models.ManyToManyField(Fine, blank=True)
    

    def save(self, *args, **kwargs):
        if self.role == 'SUPERUSER':
            self.is_staff = True
            self.is_superuser = True
        elif self.role == 'MANAGER':
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

class Rental(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Waiting confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    client = models.ForeignKey(User, on_delete=models.PROTECT)
    car = models.ForeignKey(Car, on_delete=models.PROTECT)
    start_date = models.DateField('Start date')
    days = models.PositiveIntegerField('Days quantity')
    expected_return_date = models.DateField('Expected return date', blank=True)
    rental_amount = models.DecimalField('Rental amount', max_digits=10, decimal_places=2, blank=True, editable = False)
    discount_amount = models.DecimalField('Discount amount', max_digits=10, decimal_places=2, default=0, editable = False)
    total_amount = models.DecimalField('Total amount', max_digits=10, decimal_places=2, blank=True, editable = False)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='PENDING', blank=True)
    fines = models.ManyToManyField(Fine, blank=True)

    def __str__(self):
        return f"Rental #{self.id} - {self.client} - {self.car}"

    @property
    def daily_rental_price(self):
        """Автоматически получаем цену из связанного автомобиля"""
        return self.car.daily_rental_price

    def save(self, *args, **kwargs):
        # Рассчитываем ожидаемую дату возврата
        if not self.expected_return_date:
            self.expected_return_date = self.start_date + datetime.timedelta(days=self.days)
        
        # Рассчитываем сумму аренды (цена из Car × количество дней)
        self.rental_amount = self.daily_rental_price * self.days
        
        # Применяем скидку, если есть промокод
        if self.promo_code:
            self.discount_amount = (self.rental_amount * self.promo_code.discount) / 100
        
        # Итоговая сумма (без штрафов)
        self.total_amount = self.rental_amount - self.discount_amount

        if self.pk:  # Проверяем, что объект уже сохранен (имеет id)
            fines_total = sum(fine.amount for fine in self.fines.all())
            self.total_amount += Decimal(str(fines_total))
    
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Rental'
        verbose_name_plural = 'Rentals'