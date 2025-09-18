from django.urls import re_path,include, path
from main import views
from django.contrib import admin, auth

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about-us/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('faq/', views.faq, name='faq'),
    path('employees/', views.employees_view, name='employees'),
    path('vacancies/', views.vacancies_view, name='vacancies'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('promocodes/', views.promocodes_view, name='promocodes'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('create_rental/', views.create_rental, name='create_rental'),
    path('cars/', views.car_list, name='car_list'),
    re_path(r'^cars/(?P<car_id>\d+)/$', views.car_detail, name='car_detail'),
    path('status-distribution/', views.status_distribution, name='status_distribution'),
    path('rental-sums-by-date/', views.rental_sums_by_date, name='rental_sums_by_date'),
    path('rentals-by-car/', views.rentals_by_car, name='rentals_by_car'),
    path('redact_rental/<int:rental_id>/', views.redact_rental, name='redact_rental'),
    path('delete_rental/<int:rental_id>/', views.delete_rental, name='delete_rental'),
    path('clients-with-rentals/', views.clients_with_rentals, name='clients_with_rentals'),
    path('view-user-profile/<int:user_id>/', views.view_user_profile, name='view_user_profile'), 
    path('rental-profit/', views.rental_profit, name='rental_profit'),
]