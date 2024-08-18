from django.contrib import admin
from posApp.models import Category, Products, Sales, salesItems,Userinfo 

# Register your models here.
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Sales)
admin.site.register(salesItems)
#admin.site.register(Employees)
admin.site.register((Userinfo,))