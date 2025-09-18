from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from .models import News, FAQ, Employee, Vacancy, Review, PromoCode, Rental, Car
from django.utils import timezone
from .forms import UserRegisterForm, RentalForm
import datetime
import calendar
from django.db.models import Count, Sum
from datetime import timedelta
import requests
import logging
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import User, Rental
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from .models import User, Rental
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# Настройки по умолчанию
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
    logger.debug("Загрузка главной страницы")
    cat_fact = get_cat_fact_with_fallback()
    news = News.objects.order_by('id')[:1]
    logger.info("Главная страница успешно загружена")
    return render(request, 'main/index.html', {'news': news, 'cat_fact': cat_fact, 'api_works': cat_fact != DEFAULT_CAT_FACT})


def status_distribution(request):
    status_counts = Rental.objects.values('status').annotate(count=Count('status')).order_by('status')
    status_data = {entry['status']: entry['count'] for entry in status_counts}
    max_count = max(status_data.values(), default=1)
    status_bars = {}
    for status, count in status_data.items():
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
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    rental_sums = Rental.objects.filter(start_date__range=[start_date, end_date]) \
        .values('start_date') \
        .annotate(total=Sum('total_amount')) \
        .order_by('start_date')
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
    car_rentals = Rental.objects.values('car__model__name').annotate(count=Count('car')).order_by('car__model__name')
    print("DEBUG: car_rentals =", list(car_rentals))
    print("DEBUG: All Rentals with Cars:", Rental.objects.select_related('car__model').all())
    
    if not car_rentals:
        return render(request, 'main/rentals_by_car.html', {
            'error_message': 'Нет данных об арендах. Убедитесь, что в базе данных есть записи в модели Rental и связанные автомобили.'
        })
    
    car_rentals = [r for r in car_rentals if r['car__model__name']]
    
    if not car_rentals:
        return render(request, 'main/rentals_by_car.html', {
            'error_message': 'Нет данных об арендах с определённой моделью автомобиля.'
        })
    
    max_count = max(entry['count'] for entry in car_rentals)
    if max_count == 0:
        max_count = 1
    
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
    car = get_object_or_404(Car, pk=car_id)
    return render(request, 'main/car_detail.html', {'car': car})

def create_rental(request):
    user_timezone = timezone.get_current_timezone()
    current_date = timezone.now().astimezone(user_timezone)
    cal = calendar.monthcalendar(current_date.year, current_date.month)
    
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            promo_code = form.cleaned_data.get('promo_code_input')  # Исправлено здесь
            
            rental = Rental(
                client=request.user,
                car=form.cleaned_data['car'],
                start_date=form.cleaned_data['start_date'],
                days=form.cleaned_data['days'],
                promo_code=promo_code,  # promo_code будет None, если не указан
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

@login_required
def redact_rental(request, rental_id):
    logger.debug(f"Редактирование аренды #{rental_id} пользователем {request.user.username}")
    rental = get_object_or_404(Rental, id=rental_id, client=request.user)
    user_timezone = timezone.get_current_timezone()
    current_date = timezone.now().astimezone(user_timezone)
    cal = calendar.monthcalendar(current_date.year, current_date.month)

    if request.method == 'POST':
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            promo_code = form.cleaned_data.get('promo_code_input')
            rental.car = form.cleaned_data['car']
            rental.start_date = form.cleaned_data['start_date']
            rental.days = form.cleaned_data['days']
            rental.promo_code = promo_code
            rental.save()
            logger.info(f"Аренда #{rental.id} отредактирована")
            return redirect('profile')
        else:
            logger.warning(f"Ошибка редактирования аренды: {form.errors}")

    else:
        form = RentalForm(instance=rental)

    return render(request, 'main/redact_rental.html', {
        'form': form,
        'current_date': current_date.strftime('%d/%m/%Y'),
        'user_timezone': user_timezone,
        'calendar': cal,
        'rental': rental,
    })


@login_required
def delete_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, client=request.user)
    if request.method == 'POST':
        logger.info(f"Аренда #{rental.id} удалена пользователем {request.user.username}")
        rental.delete()
        return redirect('profile')
    return render(request, 'main/delete_rental.html', {'rental': rental})

def role_check(role):
    return user_passes_test(lambda u: u.role == role)

@login_required
def profile(request):
    logger.debug(f"Загрузка профиля пользователя {request.user.username}")
    user = request.user
    rentals = Rental.objects.filter(client=user).order_by('-start_date')
    promocodes = user.promocodes.all()

    search_query = request.GET.get('promo_search')
    if search_query:
        promocodes = promocodes.filter(code__icontains=search_query)

    sort = request.GET.get('sort')
    order = request.GET.get('order')

    if sort == 'code':
        if order == 'desc':
            promocodes = promocodes.order_by('-code')
        else:
            promocodes = promocodes.order_by('code')

    return render(request, 'main/profile.html', {
        'user': user,
        'rentals': rentals,
        'promocodes': promocodes,
    })

def register(request):
    logger.debug("Регистрация нового пользователя")
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'CLIENT'
            user.save()
            logger.info(f"Зарегистрирован новый пользователь: {user.username}")
            return redirect('login')
        else:
            logger.warning(f"Ошибка регистрации: {form.errors}")
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'main/login.html'
    redirect_authenticated_user = True
    redirect_field_name = 'next'

class CustomLogoutView(LogoutView):
    next_page = 'login'

def about(request):
    logger.debug("Загрузка страницы 'О нас'")
    return render(request, "main/about.html")

def news(request):
    logger.debug("Загрузка новостей")
    all_news = News.objects.all()
    return render(request, "main/news.html", {'news': all_news})

def faq(request):
    logger.debug("Загрузка FAQ")
    faqs = FAQ.objects.all()
    return render(request, "main/faq.html", {'faqs': faqs})

def employees_view(request):
    logger.debug("Загрузка страницы сотрудников")
    employees = Employee.objects.all()
    return render(request, 'main/employees.html', {'employees': employees})

def vacancies_view(request):
    logger.debug("Загрузка вакансий")
    vacancies = Vacancy.objects.filter(is_active=True)
    return render(request, 'main/vacancies.html', {'vacancies': vacancies})


def reviews_view(request):
    logger.debug("Загрузка отзывов")
    if request.method == 'POST' and request.user.is_authenticated:
        Review.objects.create(
            user=request.user,
            name=request.user.get_full_name() or request.user.username,
            rating=request.POST.get('rating'),
            text=request.POST.get('text'),
            is_published=True
        )
        logger.info(f"Пользователь {request.user.username} оставил отзыв")
    reviews = Review.objects.filter(is_published=True)
    return render(request, "main/reviews.html", {'reviews': reviews})

def promocodes_view(request):
    logger.debug("Загрузка страницы промокодов")
    sort_by = request.GET.get('sort', 'code')
    active_promos = PromoCode.objects.all().order_by(sort_by)
    return render(request, 'main/promocodes.html', {'active_promos': active_promos})

def privacy_view(request):
    logger.debug("Загрузка политики конфиденциальности")
    return render(request, 'main/privacy.html')

def car_list(request):
    logger.debug("Загрузка списка автомобилей")
    search_query = request.GET.get('search', '')
    if search_query:
        cars = Car.objects.filter(license_plate__icontains=search_query)
    else:
        cars = Car.objects.all()
    return render(request, 'main/car_list.html', {'cars': cars})


@login_required
@user_passes_test(lambda u: u.role in ['MANAGER', 'SUPERUSER'])
def clients_with_rentals(request):
    logger.debug("Загрузка списка клиентов с арендами")
    clients = User.objects.filter(role='CLIENT', rental__isnull=False).distinct()\
        .annotate(rental_count=Count('rental'))
    if not clients.exists():
        logger.warning("Нет клиентов с арендами")
        return render(request, 'main/clients_with_rentals.html', {
            'error_message': 'Нет клиентов с арендами.'
        })
    return render(request, 'main/clients_with_rentals.html', {'clients': clients})

@login_required
@user_passes_test(lambda u: u.role in ['MANAGER', 'SUPERUSER'])
def view_user_profile(request, user_id):
    logger.debug(f"Просмотр профиля пользователя с ID {user_id}")
    user = get_object_or_404(User, id=user_id)
    rentals = Rental.objects.filter(client=user).order_by('-start_date')
    if request.method == 'POST':
        rental_id = request.POST.get('rental_id')
        new_status = request.POST.get('status')
        if rental_id and new_status in dict(Rental.STATUS_CHOICES).keys():
            rental = get_object_or_404(Rental, id=rental_id, client=user)
            rental.status = new_status
            rental.save()
            logger.info(f"Статус аренды #{rental.id} обновлён на {new_status}")
            return redirect('view_user_profile', user_id=user.id)
    return render(request, 'main/view_user_profile.html', {
        'viewed_user': user,
        'rentals': rentals,
        'status_choices': Rental.STATUS_CHOICES,
    })

@login_required
@user_passes_test(lambda u: u.role in ['MANAGER', 'SUPERUSER'])
def rental_profit(request):
    confirmed_rentals = Rental.objects.filter(status__in=['CONFIRMED', 'ACTIVE', 'COMPLETED'])
    pending_rentals = Rental.objects.filter(status='PENDING')
    total_profit = sum(r.total_amount for r in confirmed_rentals) or Decimal('0.00')
    logger.info(f"Просмотр прибыли от аренды пользователем {request.user.username}: {total_profit}")
    return render(request, 'main/rental_profit.html', {
        'total_profit': total_profit,
        'confirmed_rentals': confirmed_rentals,
        'pending_rentals': pending_rentals,
    })