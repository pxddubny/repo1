from django.contrib import admin
from .models import News, FAQ, Employee, Vacancy, Review, PromoCode


admin.site.register(News)
admin.site.register(FAQ)
admin.site.register(Employee)
admin.site.register(Vacancy)
admin.site.register(Review)
admin.site.register(PromoCode)