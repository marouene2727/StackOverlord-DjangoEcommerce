from django.contrib import admin

from .models import Order, Product, Category, Review


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Order)

