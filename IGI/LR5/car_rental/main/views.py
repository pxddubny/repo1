from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from .models import News, FAQ, Employee, Vacancy, Review, PromoCode, Rental, Car
from django.utils import timezone
from .forms import UserRegisterForm
from .forms import RentalForm
import datetime
import calendar
from django.db.models import Count, Sum
from datetime import timedelta
import requests
import logging

logger = logging.getLogger(__name__)

# Настройки по умолчанию (если нет в settings.py)
DEFAULT_CAT_FACT = "Стандартный факт: Коты любят спать до 16 часов в день."

def get_cat_fact_with_fallback():
    try:
        response = requests.get(
            'https://catfact.ninja/fact',
            timeout=3,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response.raise_for_status()
        return response.json().get('fact', DEFAULT_CAT_FACT)
    except Exception as e:
        logger.error(f"CatFact API error: {str(e)}")
        return DEFAULT_CAT_FACT

def index(request):
    cat_fact = get_cat_fact_with_fallback()
    news = News.objects.order_by('id')[:1]
    return render(request, 'main/index.html', {
        'news': news,
        'cat_fact': cat_fact,
        'api_works': cat_fact != DEFAULT_CAT_FACT
    })

def status_distribution(request):
    # Подсчёт количества аренд по статусам
    status_counts = Rental.objects.values('status').annotate(count=Count('status')).order_by('status')
    # Преобразуем в словарь для удобства
    status_data = {entry['status']: entry['count'] for entry in status_counts}
    # Максимальное значение для масштабирования псевдографики
    max_count = max(status_data.values(), default=1)
    # Создаём данные для псевдографики
    status_bars = {}
    for status, count in status_data.items():
        # Ищем человекочитаемое название статуса в STATUS_CHOICES
        status_label = status
        for code, label in Rental.STATUS_CHOICES:
            if code == status:
                status_label = label
                break
        status_bars[status_label] = {
            'count': count,
            'bar': '█' * int(count * 20 / max_count)
        }
    return render(request, 'main/status_distribution.html', {'status_bars': status_bars})

def rental_sums_by_date(request):
    # Данные за последние 7 дней
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    rental_sums = Rental.objects.filter(start_date__range=[start_date, end_date]) \
        .values('start_date') \
        .annotate(total=Sum('total_amount')) \
        .order_by('start_date')
    # Максимальная сумма для масштабирования
    max_total = max((entry['total'] for entry in rental_sums), default=1)
    sums_data = [
        {
            'date': entry['start_date'].strftime('%Y-%m-%d'),
            'total': float(entry['total']),
            'bar': '█' * int(float(entry['total']) * 20 / float(max_total))
        }
        for entry in rental_sums
    ]
    return render(request, 'main/rental_sums_by_date.html', {'sums_data': sums_data})

def rentals_by_car(request):
    # Подсчёт аренд по автомобилям (используем car__model__name для получения названия модели)
    car_rentals = Rental.objects.values('car__model__name').annotate(count=Count('car')).order_by('car__model__name')
    
    # Отладочная информация
    print("DEBUG: car_rentals =", list(car_rentals))
    print("DEBUG: All Rentals with Cars:", Rental.objects.select_related('car__model').all())
    
    # Если данных нет, передаём сообщение об ошибке
    if not car_rentals:
        return render(request, 'main/rentals_by_car.html', {
            'error_message': 'Нет данных об арендах. Убедитесь, что в базе данных есть записи в модели Rental и связанные автомобили.'
        })
    
    # Фильтруем только записи с непустым car__model__name
    car_rentals = [r for r in car_rentals if r['car__model__name']]
    
    if not car_rentals:
        return render(request, 'main/rentals_by_car.html', {
            'error_message': 'Нет данных об арендах с определённой моделью автомобиля.'
        })
    
    # Максимальное количество аренд для масштабирования псевдографики
    max_count = max(entry['count'] for entry in car_rentals)
    if max_count == 0:
        max_count = 1  # Избегаем деления на 0
    
    # Формируем данные для шаблона
    car_data = [
        {
            'car': entry['car__model__name'] if entry['car__model__name'] else 'Неизвестный автомобиль',
            'count': entry['count'],
            'bar': '█' * int(entry['count'] * 20 / max_count)
        }
        for entry in car_rentals
    ]
    
    return render(request, 'main/rentals_by_car.html', {'car_data': car_data})

def car_detail(request, car_id):
    """Детальная страница автомобиля"""
    car = get_object_or_404(Car, pk=car_id)
    return render(request, 'main/car_detail.html', {'car': car})

def create_rental(request):
    # Получаем временную зону и текущую дату
    user_timezone = timezone.get_current_timezone()
    current_date = timezone.now().astimezone(user_timezone)
    
    # Генерируем календарь
    cal = calendar.monthcalendar(current_date.year, current_date.month)
    
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            # Получаем промокод если указан
            promo_code = None
            if form.cleaned_data['promo_code']:
                try:
                    promo_code = PromoCode.objects.get(
                        code=form.cleaned_data['promo_code'],
                    )
                except PromoCode.DoesNotExist:
                    form.add_error('promo_code', "Неверный промокод")
                    return render(request, 'main/create_rental.html', context)
            
            # Создаем запись аренды
            rental = Rental(
                client=request.user,
                car=form.cleaned_data['car'],
                start_date=form.cleaned_data['start_date'],
                days=form.cleaned_data['days'],
                promo_code=promo_code,
                status='PENDING'
            )
            rental.save()
            
            return redirect('profile')
    else:
        form = RentalForm()
    
    return render(request, 'main/create_rental.html', {
        'form': form,
        'current_date': current_date.strftime('%d/%m/%Y'),
        'user_timezone': user_timezone,
        'calendar': cal,
    })

def role_check(role):
    """декоратор для проверки роли"""
    return user_passes_test(lambda u: u.role == role)

@login_required
def profile(request):
    """Profile view with rentals and promo codes"""
    user = request.user
    rentals = Rental.objects.filter(client=user).order_by('-start_date')
    
    # Get promo codes with search and sorting
    promocodes = user.promocodes.all()
    
    # Search functionality
    search_query = request.GET.get('promo_search')
    if search_query:
        promocodes = promocodes.filter(code__icontains=search_query)
    
    # Sorting functionality
    sort = request.GET.get('sort')
    order = request.GET.get('order')
    
    if sort == 'code':
        if order == 'desc':
            promocodes = promocodes.order_by('-code')
        else:
            promocodes = promocodes.order_by('code')
    
    context = {
        'user': user,
        'rentals': rentals,
        'promocodes': promocodes,
    }
    return render(request, 'main/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'CLIENT'  # по умолчанию — клиент
            user.save()
            return redirect('login')  # перенаправление на страницу входа
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'main/login.html'
    redirect_authenticated_user = True
    redirect_field_name = 'next'

class CustomLogoutView(LogoutView):
    next_page = 'login'  # перенаправление на страницу логина после выхода

def about(request):
    return render(request, "main/about.html")

def news(request):
    news = News.objects.all()
    return render(request, "main/news.html", {'news': news})

def faq(request):
    faqs = FAQ.objects.all()
    return render(request, "main/faq.html", {'faqs': faqs})

def employees_view(request):
    employees = Employee.objects.all()
    return render(request, 'main/employees.html', {'employees': employees})

def vacancies_view(request):
    vacancies = Vacancy.objects.filter(is_active=True)
    return render(request, 'main/vacancies.html', {'vacancies': vacancies})

def reviews_view(request):
    if request.method == 'POST' and request.user.is_authenticated:
        Review.objects.create(
            user=request.user,
            name=request.user.get_full_name() or request.user.username,
            rating=request.POST.get('rating'),
            text=request.POST.get('text'),
            is_published=True
        )
    
    reviews = Review.objects.filter(is_published=True)
    return render(request, 'main/reviews.html', {'reviews': reviews})

def promocodes_view(request):
    now = timezone.now().date()
    
    # Get sorting parameter
    sort_by = request.GET.get('sort', 'code')  # Default sort by code
    
    # Get active promos with sorting
    active_promos = PromoCode.objects.all().order_by(sort_by)
    
    return render(request, 'main/promocodes.html', {
        'active_promos': active_promos,
    })

def privacy_view(request):
    return render(request, 'main/privacy.html')

def car_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        cars = Car.objects.filter(license_plate__icontains=search_query)
    else:
        cars = Car.objects.all()
    return render(request, 'main/car_list.html', {'cars': cars})