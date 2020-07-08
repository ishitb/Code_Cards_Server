from django.contrib import admin
from .models import *
# Register your models here.

class CustomAccountAdmin(admin.ModelAdmin) :
    list_display = ['id', 'email']

admin.site.register(Account, CustomAccountAdmin)