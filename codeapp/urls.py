from django.urls import path, include
from .views import registration_view, Login, Reset_Password
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'codeapp'

from django.contrib.auth import views as auth_views

auth_view_urls = [
	path('reset_password/', auth_views.PasswordResetView.as_view(), name="reset_password"),
	path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
	path('reset/(?P<uidb65>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,23})/', auth_views.PasswordResetConfirmView.as_view(), name="password_rest_confirm"),
	path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

urlpatterns = [
	path('register', registration_view, name='register'),
	path('login', Login, name='login'),
] + auth_view_urls