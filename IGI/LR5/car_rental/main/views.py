from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from .models import News, FAQ, Employee, Vacancy, Review, PromoCode
from django.utils import timezone
from .forms import UserRegisterForm

def role_check(role):
    """декоратор для проверки роли"""
    return user_passes_test(lambda u: u.role == role)

@role_check('SUPERUSER')
def admin_dashboard(request):
    """только для владельца"""
    return render(request, 'admin_dash.html')

@login_required
def profile(request):
    """для всех авторизованных"""
    user = request.user
    rentals = []  # временная заглушка, так как модель Rental не определена
    return render(request, 'main/profile.html', {'user': user, 'rentals': rentals})

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
    now = timezone.now()
    active_promos = PromoCode.objects.filter(is_active=True, end_date__gte=now)
    expired_promos = PromoCode.objects.filter(end_date__lt=now)
    return render(request, 'main/promocodes.html', {
        'active_promos': active_promos,
        'expired_promos': expired_promos
    })

def privacy_view(request):
    return render(request, 'main/privacy.html')