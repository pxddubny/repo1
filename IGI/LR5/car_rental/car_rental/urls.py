from django.urls import path
from main import views
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index),
    path("about-us", views.about),
    path("news", views.news),
    path("faq", views.faq),
    path('employees/', views.employees_view, name='employees'),
    path('vacancies/', views.vacancies_view, name='vacancies'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('promocodes/', views.promocodes_view, name='promocodes'),
    path('privacy/', views.privacy_view, name='privacy'),
]