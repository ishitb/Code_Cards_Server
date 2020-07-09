from django.urls import path
from .views import registration_view, Login, OAuthLogin, OAuthLogin_detail, RequestResetPasswordView, ContactUsViewSet
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

app_name = 'codeapp'

from django.contrib.auth import views as auth_views

# BY REST_FRAMEWORK
router = DefaultRouter()
router.register('contact-us', ContactUsViewSet, basename="Contact Us Queries")

auth_view_urls = [
	path('reset_password/', RequestResetPasswordView.as_view(), name="reset_password"),
	path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
	path('reset/(?P<uidb65>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,23})/', auth_views.PasswordResetConfirmView.as_view(), name="password_rest_confirm"),
	path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

urlpatterns = [
	path('register', registration_view, name='register'),
	path('login', Login, name='login'),
	path('oauthLogin', OAuthLogin, name='oauthLogin'),
	path('oauthLoginDetail/<int:pk>/', OAuthLogin_detail, name='oauthLoginDetail'),
] + auth_view_urls + router.urls

# FOR IMAGES
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = urlpatterns + static(settings.CONTACT_US_MEDIA_URL, document_root=settings.CONTACT_US_MEDIA_ROOT)