from django.contrib import admin
from .models import User, Country, Centre, Category, SubCategory, SubCategory

admin.site.register(User)
admin.site.register(Country)
admin.site.register(Centre)
admin.site.register(Category)
admin.site.register(SubCategory)
