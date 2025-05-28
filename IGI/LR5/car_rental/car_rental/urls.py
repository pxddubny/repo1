from django.urls import path,include
from main import views
from django.contrib import admin, auth

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('faq/', views.faq, name='faq'),
    path('employees/', views.employees_view, name='employees'),
    path('vacancies/', views.vacancies_view, name='vacancies'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('promocodes/', views.promocodes_view, name='promocodes'),
    path('privacy/', views.privacy_view, name='privacy')
]