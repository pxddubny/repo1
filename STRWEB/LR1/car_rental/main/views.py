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
from .models import User, Rental, Partner
from decimal import Decimal
import logging
import matplotlib.pyplot as plt
import base64
from io import BytesIO

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
    cars = Car.objects.all()
    partners = Partner.objects.all()
    logger.info("Главная страница успешно загружена")
    return render(request, 'main/index.html', {'news': news, 'cat_fact': cat_fact, 'api_works': cat_fact != DEFAULT_CAT_FACT, 'cars': cars, 'partners': partners})

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

def status_distribution(request):
    try:
        status_stats = Rental.objects.values('status').annotate(count=Count('id'))
        total_rentals = Rental.objects.count()
        
        # Статистика по статусам
        completed_count = Rental.objects.filter(status='COMPLETED').count()
        active_count = Rental.objects.filter(status='ACTIVE').count()
        pending_count = Rental.objects.filter(status='PENDING').count()
        cancelled_count = Rental.objects.filter(status='CANCELLED').count()
        
        completed_percent = round((completed_count / total_rentals) * 100, 1) if total_rentals > 0 else 0
        active_percent = round((active_count / total_rentals) * 100, 1) if total_rentals > 0 else 0
        pending_percent = round((pending_count / total_rentals) * 100, 1) if total_rentals > 0 else 0
        cancelled_percent = round((cancelled_count / total_rentals) * 100, 1) if total_rentals > 0 else 0

        # График 1: Круговая диаграмма статусов
        plt.figure(figsize=(8, 6))
        status_names = [stat['status'] for stat in status_stats]
        status_counts = [stat['count'] for stat in status_stats]
        plt.pie(status_counts, labels=status_names, autopct='%1.1f%%')
        plt.title('Rental Status Distribution')
        buffer1 = BytesIO()
        plt.savefig(buffer1, format='png')
        buffer1.seek(0)
        chart_image1 = base64.b64encode(buffer1.getvalue()).decode()
        plt.close()

        # График 2: Столбчатая диаграмма статусов
        plt.figure(figsize=(10, 6))
        plt.bar(status_names, status_counts)
        plt.title('Rental Status Count')
        plt.xlabel('Status')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        buffer2 = BytesIO()
        plt.savefig(buffer2, format='png')
        buffer2.seek(0)
        chart_image2 = base64.b64encode(buffer2.getvalue()).decode()
        plt.close()

        # График 3: Средняя длительность по статусам
        duration_stats = Rental.objects.values('status').annotate(avg_duration=Avg('days'))
        plt.figure(figsize=(10, 6))
        statuses = [stat['status'] for stat in duration_stats]
        avg_durations = [stat['avg_duration'] for stat in duration_stats]
        plt.bar(statuses, avg_durations)
        plt.title('Average Rental Duration by Status')
        plt.xlabel('Status')
        plt.ylabel('Average Days')
        plt.xticks(rotation=45)
        buffer3 = BytesIO()
        plt.savefig(buffer3, format='png')
        buffer3.seek(0)
        chart_image3 = base64.b64encode(buffer3.getvalue()).decode()
        plt.close()

        context = {
            'total_rentals': total_rentals,
            'completed_count': completed_count,
            'active_count': active_count,
            'pending_count': pending_count,
            'cancelled_count': cancelled_count,
            'completed_percent': completed_percent,
            'active_percent': active_percent,
            'pending_percent': pending_percent,
            'cancelled_percent': cancelled_percent,
            'chart_image1': chart_image1,
            'chart_image2': chart_image2,
            'chart_image3': chart_image3
        }
        
    except Exception as e:
        context = {'error_message': str(e)}
    
    return render(request, 'main/status_distribution.html', context)

def rentals_by_car(request):
    try:
        car_stats = Rental.objects.values('car__model__name').annotate(count=Count('car')).order_by('-count')[:10]
        total_rentals = Rental.objects.count()
        unique_cars = car_stats.count()
        avg_rentals = round(total_rentals / unique_cars, 2) if unique_cars > 0 else 0

        # График 1: Аренды по моделям
        plt.figure(figsize=(12, 6))
        car_names = [stat['car__model__name'] for stat in car_stats]
        counts = [stat['count'] for stat in car_stats]
        plt.bar(car_names, counts)
        plt.xticks(rotation=45)
        plt.tight_layout()
        buffer1 = BytesIO()
        plt.savefig(buffer1, format='png')
        buffer1.seek(0)
        chart_image1 = base64.b64encode(buffer1.getvalue()).decode()
        plt.close()

        # График 2: Распределение длительности аренд
        durations = list(Rental.objects.values_list('days', flat=True))
        plt.figure(figsize=(10, 6))
        plt.hist(durations, bins=20, edgecolor='black')
        plt.xlabel('Days')
        plt.ylabel('Frequency')
        buffer2 = BytesIO()
        plt.savefig(buffer2, format='png')
        buffer2.seek(0)
        chart_image2 = base64.b64encode(buffer2.getvalue()).decode()
        plt.close()

        # График 3: Статусы аренд
        status_stats = Rental.objects.values('status').annotate(count=Count('id'))
        status_names = [stat['status'] for stat in status_stats]
        status_counts = [stat['count'] for stat in status_stats]
        plt.figure(figsize=(8, 6))
        plt.pie(status_counts, labels=status_names, autopct='%1.1f%%')
        buffer3 = BytesIO()
        plt.savefig(buffer3, format='png')
        buffer3.seek(0)
        chart_image3 = base64.b64encode(buffer3.getvalue()).decode()
        plt.close()

        # График 4: Топ-5 автомобилей
        top_cars = car_stats[:5]
        plt.figure(figsize=(10, 6))
        plt.bar([stat['car__model__name'] for stat in top_cars], [stat['count'] for stat in top_cars])
        plt.xticks(rotation=45)
        plt.tight_layout()
        buffer4 = BytesIO()
        plt.savefig(buffer4, format='png')
        buffer4.seek(0)
        chart_image4 = base64.b64encode(buffer4.getvalue()).decode()
        plt.close()

        context = {
            'total_rentals': total_rentals,
            'unique_cars': unique_cars,
            'avg_rentals': avg_rentals,
            'chart_image1': chart_image1,
            'chart_image2': chart_image2,
            'chart_image3': chart_image3,
            'chart_image4': chart_image4
        }
        
    except Exception as e:
        context = {'error_message': str(e)}
    
    return render(request, 'main/rentals_by_car.html', context)

def car_detail(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    return render(request, 'main/car_detail.html', {'car': car})

@login_required
def payment_page(request, rental_id):
    """Страница оплаты аренды"""
    rental = get_object_or_404(Rental, id=rental_id, client=request.user, status='PENDING')
    return render(request, 'main/payment.html', {'rental': rental})

@login_required
def payment_all_page(request):
    """Страница оплаты всей корзины"""
    cart_items = Rental.objects.filter(client=request.user, status='PENDING')
    
    if not cart_items:
        return redirect('profile')
    
    total_amount = sum(rental.total_amount for rental in cart_items)
    
    return render(request, 'main/payment_all.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

@login_required
def process_payment_all(request):
    """Обработка оплаты всей корзины"""
    cart_items = Rental.objects.filter(client=request.user, status='PENDING')
    
    if not cart_items:
        return redirect('profile')
    
    if request.method == 'POST':
        for rental in cart_items:
            rental.status = 'CONFIRMED'
            rental.is_paid = True
            rental.save()
        
        logger.info(f"Вся корзина оплачена пользователем {request.user.username}")
        return redirect('profile')
    
    return redirect('payment_all_page')

@login_required
def process_payment(request, rental_id):
    """Обработка оплаты"""
    rental = get_object_or_404(Rental, id=rental_id, client=request.user, status='PENDING')
    
    if request.method == 'POST':
        rental.status = 'CONFIRMED'
        rental.is_paid = True
        rental.save()
        logger.info(f"Аренда #{rental.id} оплачена пользователем {request.user.username}")
        return redirect('profile')
    
    return redirect('payment_page', rental_id=rental_id)

def create_rental(request):
    user_timezone = timezone.get_current_timezone()
    current_date = timezone.now().astimezone(user_timezone)
    cal = calendar.monthcalendar(current_date.year, current_date.month)
    
    # Получаем car_id из GET параметров
    car_id = request.GET.get('car_id')
    initial_data = {}
    
    if car_id:
        try:
            car = get_object_or_404(Car, pk=car_id)
            initial_data['car'] = car
        except (ValueError, Car.DoesNotExist):
            pass
    
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            promo_code = form.cleaned_data.get('promo_code_input')
            rental = Rental(
                client=request.user,
                car=form.cleaned_data['car'],
                start_date=form.cleaned_data['start_date'],
                days=form.cleaned_data['days'],
                status='PENDING'
            )
            # Устанавливаем промокод только если он есть
            if promo_code:
                rental.promo_code = promo_code
            rental.save()
            return redirect('profile')
    else:
        form = RentalForm(initial=initial_data)
    
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
            # Устанавливаем промокод только если он есть
            if promo_code:
                rental.promo_code = promo_code
            else:
                rental.promo_code = None  # Явно устанавливаем None если промокода нет
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
    
    # Корзина = PENDING статус
    cart_items = Rental.objects.filter(client=user, status='PENDING')
    cart_count = cart_items.count()
    
    # Заказы = все кроме PENDING
    orders = Rental.objects.filter(client=user).exclude(status='PENDING').order_by('-start_date')
    
    promocodes = user.promocodes.all()
    search_query = request.GET.get('promo_search')
    if search_query:
        promocodes = promocodes.filter(code__icontains=search_query)

    return render(request, 'main/profile.html', {
        'user': user,
        'cart_items': cart_items,
        'cart_count': cart_count,
        'orders': orders,
        'promocodes': promocodes,
    })

@login_required
def checkout_rental(request, rental_id):
    """Оплатить одну аренду из корзины"""
    rental = get_object_or_404(Rental, id=rental_id, client=request.user, status='PENDING')
    rental.status = 'CONFIRMED'
    rental.save()
    return redirect('profile')

@login_required
def checkout_all(request):
    """Оплатить всю корзину"""
    cart_items = Rental.objects.filter(client=request.user, status='PENDING')
    
    if not cart_items:
        return redirect('profile')
    
    for rental in cart_items:
        rental.status = 'CONFIRMED'
        rental.save()
    
    return redirect('profile')

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
            logger.warning(f"О  ибка регистрации: {form.errors}")
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