from django.urls import path
from .views import registration_view, Login, RequestResetPasswordView, ContactUsViewSet, Update_Account, CardsListView, CardsSolutionsView, CardsView, NotesViewSet, BookmarksViewSet,Get_Page, ListContestsView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

app_name = 'codeapp'

from django.contrib.auth import views as auth_views
from .forms.password_reset_confirm import SetPasswordForm

# BY REST_FRAMEWORK
router = DefaultRouter()
router.register('contact-us', ContactUsViewSet, basename="Contact Us Queries")
# router.register('cards/',CardsView)
router.register('cards-solutions', CardsSolutionsView, basename="Cards Solutions")
router.register('notes', NotesViewSet, basename="Notes")
router.register('bookmarks', BookmarksViewSet, basename="Bookmarks")

auth_view_urls = [
	path('reset_password/', RequestResetPasswordView.as_view(), name="reset_password"),
	path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
	path(
		'reset/<uidb64>/<token>/',
     	auth_views.PasswordResetConfirmView.as_view(
			template_name="codeapp/password_reset_confirm.html",
			form_class=SetPasswordForm
		), 
     	name="password_reset_confirm"
	),
	path(
		'reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(
			template_name="codeapp/password_reset_complete.html"
		), 
        name="password_reset_complete"
	),
]

urlpatterns = [
	path('register', registration_view, name='register'),
	path('contestAPI',ListContestsView.as_view(),name = 'contests'),
	path('login', Login, name='login'),
	path('update-account/', Update_Account, name="Update Account"),
	path('get-page/', Get_Page, name="Page Details"),
	# path('oauthLogin', OAuthLogin, name='oauthLogin'),
	# path('oauthLoginDetail/<int:pk>/', OAuthLogin_detail, name='oauthLoginDetail'),
	path('cards', CardsView, name='cards'),
	path('cards/list', CardsListView.as_view(), name='cardsList'),
	# path('cards/solutions', CardsSolutionsView, name='cardsSolutions'),
] + auth_view_urls + router.urls

# FOR IMAGES
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = urlpatterns + static(settings.CONTACT_US_MEDIA_URL, document_root=settings.CONTACT_US_MEDIA_ROOT)