from rest_framework import serializers

from .models import *

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils.mails import send


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'username', 'password', 'password2', 'avatar']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):

        account = Account(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            avatar = self.validated_data['avatar']
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError(
                {'error_message': 'Passwords must match.'})
        account.set_password(password)
        account.save()
        return account

class OAuthAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthAccount
        fields = ['id','email', 'username', 'avatar',
                  'date_joined', 'oauthType', 'token', 'is_admin']

class ContactUsSerializer(serializers.ModelSerializer) :
    class Meta :
        model = ContactUsModel
        fields = ['name', 'email', 'screenshot', 'details', 'id']

# PASSWORD RESET SERIALIZER
class RequestResetPasswordSerializer(serializers.Serializer) :


    email = serializers.EmailField(min_length=2)

    class Meta :
        fields = ['email']

    def validate(self, attrs) :
        email = attrs.get('email')
        try :
            self.account = Account.objects.filter(email = email)[0]
            return self.account
        
        except :
            raise serializers.ValidationError(
                {'error': "User with this Email Address doesn't exist. Please try again!"}
            )

    def encrypt(self) :
        self.token = default_token_generator.make_token(self.account)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.account.pk))

    def send_mail(self, request) :
        self.current_site = get_current_site(request)
        self.link = str(self.current_site) + '/reset/' + self.uidb64 + '/' + self.token + '/'
        subject = f"Password reset for '{str(self.account)}'"
        message = f"Please go to this link to reset your password: {self.link}"
        send(subject, message, [str(self.account)])

    def send_link(self, request) :
        self.encrypt()
        self.send_mail(request)
        return self.account


class CardsSolutionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardsSolutions
        fields = ['solution','timeComplexity']

class CardsSerializer(serializers.ModelSerializer):
    solutions = CardsSolutionsSerializer(read_only=True, many=True)
    
    class Meta:
        model = Cards
        fields = ['question','hint','company','tags','solutions']

    # def create(self, validated_data):
    #     solutions_data = validated_data.pop('solutions')
    #     cards = Cards.objects.create(**validated_data)
    #     for solutions_data in solutions_data:
    #         CardsSolutions.objects.create(question=cards, **solutions_data)
    #     return cards