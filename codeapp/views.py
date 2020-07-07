from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, OAuthAccountSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from .models import Account, OAuthAccount
from django.http import HttpResponse


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
            return Response({'data': serializer.errors}, status=status.HTTP_409_CONFLICT)
        return Response(data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((AllowAny,))
def Login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(email=email, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials', 'status': 'fail'})
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
        return Respose(status=status.HTTP_204_NO_CONNECT)
