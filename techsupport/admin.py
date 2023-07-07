from django.contrib import admin
from .models import User, UserProfile, Country, Centre, Category, SubCategory, SubCategory, Settings, Region

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(Centre)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Settings)
