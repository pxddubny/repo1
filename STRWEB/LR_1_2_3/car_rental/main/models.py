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

class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название компании")
    about = models.TextField(verbose_name="О компании")
    logo = models.ImageField(upload_to='static/info/', verbose_name="Логотип", blank=True)
    
    video = models.FileField(upload_to='static/info/', verbose_name="Видео", blank=True)
    
    # История
    history = models.TextField(verbose_name="История компании", blank=True, 
                              help_text="Пишите историю по годам: 2020 - начали работу, 2022 - открыли новый офис")
    
    address = models.TextField(verbose_name="Адрес", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)
    
    certificate = models.ImageField(upload_to='static/info/', verbose_name="Сертификат", blank=True)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компания"

    def __str__(self):
        return self.name

class Partner(models.Model):
    name = models.CharField('name', max_length=200)
    website = models.URLField('website')
    logo = models.ImageField('logo', upload_to='static/partners')
    
    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
    
    def __str__(self):
        return self.name

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
            self.is_staff = False
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

class PaidRentalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_paid=True)

class CartRentalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_paid=False)

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
    rental_amount = models.DecimalField('Rental amount', max_digits=10, decimal_places=2, blank=True, editable=False)
    discount_amount = models.DecimalField('Discount amount', max_digits=10, decimal_places=2, default=0, editable=False)
    total_amount = models.DecimalField('Total amount', max_digits=10, decimal_places=2, blank=True, editable=False)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='PENDING', blank=True)
    fines = models.ManyToManyField(Fine, blank=True)
    is_paid = models.BooleanField('Paid', default=False)  # Новое поле!

    def __str__(self):
        return f"Rental #{self.id} - {self.client} - {self.car}"

    @property
    def daily_rental_price(self):
        return self.car.daily_rental_price

    def clean(self):
        """Валидация даты начала аренды"""
        #if self.start_date < timezone.now().date():
         #   raise ValidationError('Start date cannot be in the past')
        
        # Проверяем, что expected_return_date установлен
        if not self.expected_return_date:
            # Если не установлен, рассчитываем его
            self.expected_return_date = self.start_date + datetime.timedelta(days=self.days)
        
        # Проверка доступности автомобиля (только для новых или измененных аренд)
        if self._state.adding or self.has_changed(['start_date', 'days', 'car']):
            overlapping_rentals = Rental.objects.filter(
                car=self.car,
                start_date__lte=self.expected_return_date,
                expected_return_date__gte=self.start_date,
                status__in=['CONFIRMED', 'ACTIVE', 'PENDING'],
                is_paid=True  # Только оплаченные аренды
            ).exclude(id=self.id)
            
            if overlapping_rentals.exists():
                raise ValidationError('Car is not available on selected dates')
            
    def has_changed(self, fields):
        """Проверяет, изменились ли указанные поля"""
        if not self.pk:
            return False
        old = Rental.objects.get(pk=self.pk)
        return any(getattr(old, field) != getattr(self, field) for field in fields)

    def save(self, *args, **kwargs):
        # Рассчитываем ожидаемую дату возврата
        if not self.expected_return_date:
            self.expected_return_date = self.start_date + datetime.timedelta(days=self.days)
        
        # Рассчитываем сумму аренды
        self.rental_amount = self.daily_rental_price * self.days
        
        # Применяем скидку
        if self.promo_code:
            self.discount_amount = (self.rental_amount * self.promo_code.discount) / 100
        else:
            self.discount_amount = Decimal('0.00')
        
        # Итоговая сумма
        self.total_amount = self.rental_amount - self.discount_amount

        if self.pk:
            fines_total = sum(float(fine.fine) for fine in self.fines.all())
            self.total_amount += Decimal(str(fines_total))
        
        # Валидация перед сохранением
        try:
            self.clean()
        except ValidationError as e:
            # Если возникает ошибка валидации, можно либо выбросить исключение,
            # либо обработать его в зависимости от вашей логики
            raise e
        
        super().save(*args, **kwargs)

    def mark_as_paid(self):
        """Метод для отметки аренды как оплаченной"""
        self.is_paid = True
        self.status = 'CONFIRMED'
        self.save()

    class Meta:
        verbose_name = 'Rental'
        verbose_name_plural = 'Rentals'