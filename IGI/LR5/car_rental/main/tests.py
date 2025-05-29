from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import User, Car, Rental, PromoCode, CarModel

import datetime

User = get_user_model()

class RentalModelTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='testclient',
            password='password',
            role='CLIENT',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='2000-01-01'
        )

        self.car_model = CarModel.objects.create(name='test model')
        self.car = Car.objects.create(
            license_plate='ABC123',
            model=self.car_model,
            year=2020,
            price=100000
        )

        self.promo_code = PromoCode.objects.create(
            code='DISCOUNT10',
            discount=10
        )

    def test_rental_calculations_without_promo(self):
        rental = Rental.objects.create(
            client=self.client_user,
            car=self.car,
            start_date=datetime.date(2025, 5, 1),
            days=3,
            status='PENDING'
        )
        self.assertEqual(rental.expected_return_date, datetime.date(2025, 5, 4))
        self.assertEqual(rental.rental_amount, self.car.daily_rental_price * 3)
        self.assertEqual(rental.discount_amount, Decimal('0.00'))
        self.assertEqual(rental.total_amount, rental.rental_amount)

    def test_rental_calculations_with_promo(self):
        rental = Rental.objects.create(
            client=self.client_user,
            car=self.car,
            start_date=datetime.date(2025, 5, 1),
            days=3,
            status='PENDING',
            promo_code=self.promo_code
        )
        expected_discount = rental.rental_amount * self.promo_code.discount / 100
        self.assertEqual(rental.expected_return_date, datetime.date(2025, 5, 4))
        self.assertEqual(rental.discount_amount, expected_discount)
        self.assertEqual(rental.total_amount, rental.rental_amount - expected_discount)

class RentalProfitViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='superpass',
            email='super@example.com',
            role='SUPERUSER',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='1990-01-01'
        )

        self.manager = User.objects.create_user(
            username='manager',
            password='managerpass',
            role='MANAGER',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='1995-01-01'
        )

        self.client_user = User.objects.create_user(
            username='client',
            password='clientpass',
            role='CLIENT',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='2000-01-01'
        )

        self.car_model = CarModel.objects.create(name='test car')
        self.car = Car.objects.create(
            license_plate='XYZ789',
            model=self.car_model,
            year=2020,
            price=100000
        )

        Rental.objects.create(
            client=self.client_user,
            car=self.car,
            start_date=datetime.date(2025, 5, 1),
            days=2,
            status='CONFIRMED'
        )
        Rental.objects.create(
            client=self.client_user,
            car=self.car,
            start_date=datetime.date(2025, 5, 2),
            days=1,
            status='PENDING'
        )

    def test_rental_profit_access_for_superuser(self):
        self.client.login(username='superuser', password='superpass')
        response = self.client.get(reverse('rental_profit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'total profit from confirmed rentals')

    def test_rental_profit_access_for_manager(self):
        self.client.login(username='manager', password='managerpass')
        response = self.client.get(reverse('rental_profit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'total profit from confirmed rentals')

    def test_rental_profit_access_denied_for_client(self):
        self.client.login(username='client', password='clientpass')
        response = self.client.get(reverse('rental_profit'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response['Location'])

class ClientsWithRentalsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            username='manager',
            password='managerpass',
            role='MANAGER',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='1995-01-01'
        )

        self.client_user = User.objects.create_user(
            username='client',
            password='clientpass',
            role='CLIENT',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='2000-01-01'
        )

        self.car_model = CarModel.objects.create(name='test car')
        self.car = Car.objects.create(
            license_plate='XYZ789',
            model=self.car_model,
            year=2020,
            price=100000
        )

        Rental.objects.create(
            client=self.client_user,
            car=self.car,
            start_date=datetime.date(2025, 5, 1),
            days=2,
            status='CONFIRMED'
        )

    def test_clients_with_rentals_displays_correctly(self):
        self.client.login(username='manager', password='managerpass')
        response = self.client.get(reverse('clients_with_rentals'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'client')

class AdminRestrictionsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.manager = User.objects.create_user(
            username='manager',
            password='managerpass',
            role='MANAGER',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='1995-01-01'
        )

        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='superpass',
            email='super@example.com',
            role='SUPERUSER',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='1990-01-01'
        )

        self.client_user = User.objects.create_user(
            username='client',
            password='clientpass',
            role='CLIENT',
            phone='+375 (29) 123-45-67',
            address='test address',
            birth_date='2000-01-01'
        )

        self.car_model = CarModel.objects.create(name='test car')
        self.car = Car.objects.create(
            license_plate='XYZ789',
            model=self.car_model,
            year=2020,
            price=100000
        )

        self.rental = Rental.objects.create(
            client=self.client_user,
            car=self.car,
            start_date=datetime.date(2025, 5, 1),
            days=2,
            status='CONFIRMED'
        )

    def test_manager_cannot_delete_in_admin(self):
        self.client.login(username='manager', password='managerpass')
        response = self.client.get(f'/admin/main/rental/{self.rental.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_superuser_can_delete_in_admin(self):
        self.client.login(username='superuser', password='superpass')
        response = self.client.get(f'/admin/main/rental/{self.rental.id}/delete/')
        self.assertEqual(response.status_code, 200)

class PublicViewsTests(TestCase):
    def test_public_pages_accessible(self):
        public_urls = [
            'index', 'about', 'news', 'faq', 'employees',
            'vacancies', 'reviews', 'promocodes', 'privacy', 'login', 'register'
        ]
        for url in public_urls:
            response = self.client.get(reverse(url))
            self.assertEqual(response.status_code, 200, f"{url} failed")

class RentalFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='password',
            phone='+375 (29) 123-45-67', address='Test address', birth_date='2000-01-01'
        )
        self.model = CarModel.objects.create(name='Model X')
        self.car = Car.objects.create(
            license_plate='TEST123', model=self.model, year=2020, price=100000
        )
        self.promo = PromoCode.objects.create(code='SAVE10', discount=10)

    def test_create_rental_form_valid(self):
        self.client.login(username='testuser', password='password')
        post_data = {
            'car': self.car.id,
            'days': 3,
            'start_date': timezone.now().date(),
            'promo_code_input': 'SAVE10',
        }
        response = self.client.post(reverse('create_rental'), post_data)
        self.assertEqual(response.status_code, 302)  # редирект на profile
        self.assertTrue(Rental.objects.exists())

class AccessControlTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager', password='password', role='MANAGER',
            phone='+375 (29) 123-45-67', address='addr', birth_date='1995-01-01', is_staff=True
        )
        self.client_user = User.objects.create_user(
            username='client', password='password', role='CLIENT',
            phone='+375 (29) 123-45-67', address='addr', birth_date='2000-01-01'
        )
        self.superuser = User.objects.create_superuser(
            username='admin', password='adminpass', email='a@a.com',
            phone='+375 (29) 123-45-67', address='addr', birth_date='1990-01-01'
        )
        model = CarModel.objects.create(name='Y')
        car = Car.objects.create(license_plate='ABC', model=model, year=2020, price=50000)
        self.rental = Rental.objects.create(
            client=self.client_user, car=car, start_date=timezone.now().date(), days=2
        )

    def test_rental_profit_requires_permission(self):
        self.client.login(username='client', password='password')
        response = self.client.get(reverse('rental_profit'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response['Location'])

        self.client.login(username='manager', password='password')
        response = self.client.get(reverse('rental_profit'))
        self.assertEqual(response.status_code, 200)

    def test_clients_with_rentals_requires_permission(self):
        self.client.login(username='client', password='password')
        response = self.client.get(reverse('clients_with_rentals'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='manager', password='password')
        response = self.client.get(reverse('clients_with_rentals'))
        self.assertEqual(response.status_code, 200)

    def test_delete_rental_access(self):
        self.client.login(username='client', password='password')
        response = self.client.post(reverse('delete_rental', args=[self.rental.id]))
        self.assertRedirects(response, reverse('profile'))
        self.assertFalse(Rental.objects.filter(id=self.rental.id).exists())