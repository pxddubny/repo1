from django.db import models
from django.contrib.auth.models import User

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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