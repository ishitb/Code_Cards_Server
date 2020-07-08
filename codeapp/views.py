from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, OAuthAccountSerializer, RequestResetPasswordSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from .models import Account, OAuthAccount
from django.http import HttpResponse, JsonResponse


class TestFunction(generics.GenericAPIView) :
    serializer_class = RequestResetPasswordSerializer

    def post(self, request) :
        serializer = self.serializer_class(data = request.data)
        account = serializer.is_valid(raise_exception=True)
        account = serializer.send_link(request)
        return JsonResponse({'message': f"A link to reset the password has been sent to you Email Address {str(account)}"})

@api_view(['POST', ])
def registration_view(request):

    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'successfully registered new user.'
            data['email'] = account.email
            data['username'] = account.username
            token = Token.objects.get(user=account).key
            data['token'] = token
        else:
            try :
                email_error = serializer.errors['email'][0]
            except :
                email_error = None
            
            try :
                username_error = serializer.errors['username'][0]
            except :
                username_error = None

            error_message = email_error if email_error is not None else "" + username_error if username_error is not None else ""
            return Response({'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes((AllowAny,))
def Login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(email=email, password=password)
    if not user:
        return Response({'error_message': 'Invalid Credentials'}, status = status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)

    logged_in_user = Account.objects.filter(email=user).values()[0]

    return Response({
        'email': logged_in_user.get('email'),
        'username': logged_in_user.get('username'),
        'avatar': logged_in_user.get('avatar'),
        'token': token.key
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['POST', 'GET', ])
def OAuthLogin(request):

    if request.method == 'GET':
        oauth_login = OAuthAccount.objects.all()
        serializer = OAuthAccountSerializer(oauth_login, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OAuthAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'GET', ])
def OAuthLogin_detail(request, pk):

    try:
        oauth_login = OAuthAccount.objects.get(pk=pk)
    except OAuthAccount.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OAuthAccountSerializer(oauth_login)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OAuthAccountSerializer(oauth_login, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        oauth_login.delete()
        return Response(status=status.HTTP_204_NO_CONNECT)


# CUSTOM PASSWORD RESET VIEW

from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from .forms.Password_Reset_Form import PasswordResetForm
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        return context

class PasswordResetView(PasswordContextMixin, FormView):
    email_template_name = 'registration/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'registration/password_reset_form.html'
    title = _('Password reset')
    token_generator = default_token_generator

    def list(self) :
        print(self.custom_text)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)