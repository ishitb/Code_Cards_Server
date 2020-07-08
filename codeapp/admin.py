from django.contrib import admin
from .models import *
# Register your models here.

class CustomAccountAdmin(admin.ModelAdmin) :
    list_display = ['id', 'email']

class CustomContactUsAdmin(admin.ModelAdmin) :
    list_display = ['email', 'name', 'id', 'date_posted', 'responded']

admin.site.register(Account, CustomAccountAdmin)
admin.site.register(ContactUsModel, CustomContactUsAdmin)