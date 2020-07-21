from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

import uuid

class MyAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        # if not username:
        #     raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            # username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True, null=True)
    avatar = models.CharField(max_length=50, null=True)
    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    page_offset = models.IntegerField(default=1)
    question_offset = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def getPageOffset(self):
        return self.page_offset
    
    def getQuestionOffset(self):
        return self.question_offset
        

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class OAuthAccount(models.Model):
    email = models.EmailField(max_length = 60,verbose_name = "email",null=False,blank=False)
    username = models.CharField(max_length = 30,null=False,blank=False)
    avatar = models.CharField(max_length = 50,null=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    oauthType = models.CharField(max_length = 20,null=False,blank=False)
    token = models.CharField(max_length = 50,null=False,blank=False)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email
    def getToken(self):
        return self.token
    def getUsername(self):
        return self.username

# TO SET CUSTOM FILE UPLOAD NAME
def path_and_rename(instance, filename) :
        if filename.startswith("Contact-Us-") :
            pass
        else :
            filename = "contact_us_screenshots/" + filename

        upload_to = filename
        return upload_to

class ContactUsModel(models.Model) :
    name = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 60)
    details = models.TextField()
    screenshot = models.ImageField(null = True, blank = True, upload_to=path_and_rename)
    screenshot_url = models.CharField(max_length=600, blank=True)
    date_posted = models.DateTimeField(auto_now = True)
    responded = models.BooleanField(default = False)

    def __str__(self) :
        return str(self.email)

    def add_screenshot_url(self, request) :
        if str(self.screenshot) != "" :
            screenshot_url = str(get_current_site(request)) + '/media/' + str(self.screenshot)
        else :
            screenshot_url = "No Screenshot Given!"
        return screenshot_url

# cards
class Cards(models.Model):
    question = models.TextField()
    hint = models.CharField(max_length = 600)
    company = models.CharField(max_length = 50,null=True)
    tags = models.CharField(max_length = 50,null=True)
    solution_link = models.CharField(max_length = 100, null = True)
    
    def __str__(self):
        return "Question-" + str(self.id)
    def getHint(self):
        return self.hint

class CardsSolutions(models.Model):
    # solution = models.CharField(max_length = 3000,null=False)
    solution = models.TextField()
    timeComplexity = models.CharField(max_length = 30,null = True)
    card = models.ForeignKey(Cards,on_delete = models.CASCADE)

    def __str__(self):
        return self.solution
    def getTimeComplexity(self):
        return self.timeComplexity

class Notes(models.Model) :
    title = models.CharField(max_length = 50)
    description = models.TextField()
    user = models.ForeignKey(Account, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.title)

class Bookmarks(models.Model):
    bookmark = models.ForeignKey(Cards,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.bookmark)
