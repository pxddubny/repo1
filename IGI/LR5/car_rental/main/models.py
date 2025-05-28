from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from django.conf import settings

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
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')
    is_active = models.BooleanField('active', default=True)
    created_at = models.DateTimeField('created at', auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount}%)"

    class Meta:
        verbose_name = 'Promo Code'
        verbose_name_plural = 'Promo Codes'

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
    body_type = models.OneToOneField(BodyType, on_delete=models.PROTECT)  # Пример OneToOne
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    daily_rental_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.model} ({self.license_plate})"

# 4. Парки автомобилей
class CarPark(models.Model):
    name = models.CharField(max_length=100)
    cars = models.ManyToManyField(Car)  # Пример ManyToMany

    def __str__(self):
        return self.name

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
    birth_date = models.DateField('bd date', validators=[validate_age])
    address = models.TextField('address')
    role = models.CharField('role', max_length=10, choices=ROLES, default='CLIENT')
    discount_points = models.PositiveIntegerField('discount points', default=0)

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

        