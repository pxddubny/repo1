from django.shortcuts import render
from .models import News, FAQ, Employee, Vacancy, Review, PromoCode
from django.utils import timezone



def index(request):
    news = News.objects.order_by('id')[:1]
    return render(request, 'main/index.html',{'news': news})

def about(request):
    return render(request,"main/about.html")

def news(request):
    news = News.objects.all()
    return render(request,"main/news.html", {'news': news})

def faq(request):
    faqs = FAQ.objects.all()
    return render(request,"main/faq.html", {'faqs': faqs})

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
