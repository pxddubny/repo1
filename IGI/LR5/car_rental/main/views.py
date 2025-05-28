from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from .models import News, FAQ, Employee, Vacancy, Review, PromoCode, Rental, Car
from django.utils import timezone
from .forms import UserRegisterForm
from .forms import RentalForm
import datetime
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import RentalForm
from .models import Rental, PromoCode
import datetime
import calendar


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

def index(request):
    news = News.objects.order_by('id')[:1]
    return render(request, 'main/index.html', {'news': news})

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

