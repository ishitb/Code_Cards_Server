from django.shortcuts import render
from rest_framework import status, generics, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, OAuthAccountSerializer, RequestResetPasswordSerializer, ContactUsSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from .models import Account, OAuthAccount, ContactUsModel
from django.http import HttpResponse, JsonResponse
from .utils.mails import send
from .secret import *

# PASSWORD RESET VIEW
class RequestResetPasswordView(generics.GenericAPIView) :
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

@api_view(['POST'])
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

# class ContactUsViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin) :
#     serializer_class = ContactUsSerializer
#     queryset = ContactUsModel.objects.all()

class ContactUsViewSet(viewsets.ViewSet) :
    def create(self, request) :
        serializer = ContactUsSerializer(data = request.data)

        if serializer.is_valid() :
            serializer.save()

            send("CodeCards Support Response", f"Hello {serializer.data['name']}.\nThank you for contacting us with your issue. We will try to respond to you as soon as possible and take your suggestions and comments into consideration.\nThank you for using CodeCrds.", to=[serializer.data['email']])

            query = ContactUsModel.objects.filter(pk = serializer.data['id'])
            query_screenshot_url = query[0].add_screenshot_url(request)
            query.update(screenshot_url = query_screenshot_url)

            send("New Support Query!", f"Name: {serializer.data['name']}\nEmail Address: {serializer.data['email']}\nDetails: {serializer.data['details']}\nOptional Screenshot: {query_screenshot_url}", to=[GMAIL_EMAIL])

            return Response({'message': "Query sent! Our support team will respond to you soon."}, status = status.HTTP_200_OK)
        
        else :
            return Response({'message': "There was some problem with the server. Please try again later!"}, status = status.HTTP_400_BAD_REQUEST)