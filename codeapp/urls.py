from django.urls import path
from .views import registration_view, Login
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'codeapp'

urlpatterns = [
	path('register', registration_view, name='register'),
	path('login', Login, name='login'),
]