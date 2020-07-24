from django.shortcuts import render
from rest_framework import status, generics, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, OAuthAccountSerializer, RequestResetPasswordSerializer, ContactUsSerializer, CardsSerializer, CardsSolutionsSerializer, NoteSerializer, BookmarkSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from .models import Account, OAuthAccount, ContactUsModel, Cards, CardsSolutions, Notes, Bookmarks
from django.http import HttpResponse, JsonResponse
from .utils.mails import send
from .secret import *
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

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
            data['avatar'] = account.avatar
            token = Token.objects.get(user=account).key
            data['token'] = token
            data['page_offset'] = account.page_offset
            data['question_offset'] = account.question_offset
        else:
            try :
                email_error = serializer.errors['email'][0]
            except :
                email_error = None
            
            try :
                username_error = serializer.errors['username'][0]
            except :
                username_error = None
                
            error_message = email_error if email_error is not None else "" + username_error if username_error is not None else "Internal Server Error"
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
        'token': token.key,
        'page_offset': logged_in_user.get('page_offset'),
        'question_offset': logged_in_user.get('question_offset')
    }, status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
@permission_classes((AllowAny, ))
def Get_Page(request) :

    try :
        account = Token.objects.get(key = request.data.get('token')).user
    except :
        return Response({'error_message': "Account doesn't exist. Please try again!"}, status = status.HTTP_401_UNAUTHORIZED)

    return Response({
        'page_offset': account.page_offset,
        'question_offset': account.question_offset
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['PUT'])
@permission_classes((AllowAny, ))
def Update_Account(request) :

    try :
        account = Token.objects.get(key = request.data.get('token')).user
    except :
        return Response({'error_message': "Account doesn't exist. Please try again!"}, status = status.HTTP_401_UNAUTHORIZED)
    
    if 'username' in request.data.keys() :
        newUsername = request.data.get('username')
        
        # EDGE CASES
        if account.username == newUsername :
            return Response({'error_message': "Please choose a new username!"}, status = status.HTTP_400_BAD_REQUEST)

        try :
            Account.objects.get(username = newUsername)
            return Response({'error_message': "This username already exists. Please choose a unique username!"}, status = status.HTTP_400_BAD_REQUEST)
        except :
            account.username = newUsername
    
    elif 'avatar' in request.data.keys() :
        account.avatar = request.data.get('avatar')
    
    elif 'page_offset' in request.data.keys() and 'question_offset' in request.data.keys():
        account.page_offset = request.data.get('page_offset')
        account.question_offset = request.data.get('question_offset')

    elif 'page_offset' in request.data.keys() :
        account.page_offset = request.data.get('page_offset')

    elif 'question_offset' in request.data.keys() :
        account.question_offset = request.data.get('question_offset')
    
    else :
        return Response({'error_message': "Please provide at least one field to update"}, status = status.HTTP_400_BAD_REQUEST)

    account.save()

    return Response({'message': "Account updated successfully"}, status = status.HTTP_202_ACCEPTED)

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


@api_view(['POST', 'GET', ])
def CardsView(request):

    if request.method == 'GET':
        cards = Cards.objects.all()
        serializer = CardsSerializer(cards, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CardsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CardsView(viewsets.ViewSet):
#     serializer_class = CardsSerializer
#     queryset = Cards.objects.all()


class CardsSolutionsView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin) :
    queryset = CardsSolutions.objects.all()
    serializer_class = CardsSolutionsSerializer


class CardsListView(ListAPIView):
    queryset = Cards.objects.all()
    serializer_class = CardsSerializer
    pagination_class = PageNumberPagination

# Problem 
# class CardsSolutionsListView(generics.ListCreateAPIView):
#     queryset = CardsSolutions.objects.all()
#     serializer_class = CardsSolutionsSerializer

# class CardsSolutionsView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = CardsSolutionsSerializer
#     queryset = CardsSolutions.objects.all()

class NotesViewSet(viewsets.ViewSet) :

    def get_serializer_errors(self, errors) :
        try :
            user_error = errors['user'][0]
            user_error = "User doesn't exist!"
        except :
            user_error = None
        
        try :
            title_error = errors['title'][0]
        except :
            title_error = None

        try :
            description_error = errors['description'][0]
        except :
            description_error = None
            
        error_message = user_error if user_error is not None else "" + title_error if title_error is not None else "" + description_error if description_error is not None else "" "Internal Server Error"    
        
        return error_message

    def create(self, request) :
        serializer = NoteSerializer(data = request.data)
        if serializer.is_valid() :
            serializer.save()
            
            return Response({'message': "Notes succesfully saved!"}, status = status.HTTP_201_CREATED)
        
        else :
            return Response({'error_message': self.get_serializer_errors(serializer.errors)}, status = status.HTTP_400_BAD_REQUEST)

    def list(self, request) :
        note = Notes.objects.filter(user = request.data.get('user')) if request.data.get('user') is not None else Notes.objects.all()
        serializer = NoteSerializer(note, many=True)

        return Response(serializer.data)

    def delete(self, request) :
        queryset = Notes.objects.all()
        note = get_object_or_404(queryset, pk = request.data.get('id'))

        note.delete()
        return Response({'message': "Note Successfully deleted!"}, status = status.HTTP_200_OK)

    def put(self, request) :
        queryset = Notes.objects.all()
        note = get_object_or_404(queryset, pk = request.data.get('id'))

        note.title = request.data.get('title') if request.data.get('title') is not None else note.title
        note.description = request.data.get('description') if request.data.get('description') is not None else note.description

        try :
            note.save()
            return Response({'message': "Note successfully updated!"}, status = status.HTTP_201_CREATED)
        
        except :
            return Response({'error_message': "Internal Server Error. Please try again later."}, status = status.HTTP_400_BAD_REQUEST)

class BookmarksViewSet(viewsets.ViewSet) :

    def get_serializer_errors(self, errors) :
        try :
            user_error = errors['user'][0]
            user_error = "User doesn't exist!"
        except :
            user_error = None
        
        try :
            bookmark_error = errors['bookmark'][0]
        except :
            bookmark_error = None
        
        error_message = user_error if user_error is not None else "" + bookmark_error if bookmark_error is not None else ""     
        
        return error_message

    def create(self, request) :
        data = dict()
        data['bookmark'] = int(request.data.get('cardID'))

        try :
            data['user'] = Token.objects.get(key = request.data.get('userToken')).user.id
        except:
            return Response({'error_message': "Account doesn't exist. Please try again!"}, status = status.HTTP_401_UNAUTHORIZED)

        serializer = BookmarkSerializer(data = data)
        if serializer.is_valid() :
            serializer.save()
            
            return Response({'message': "Bookmark succesfully saved!"}, status = status.HTTP_201_CREATED)
        
        else :
            return Response({'error_message': self.get_serializer_errors(serializer.errors)}, status = status.HTTP_400_BAD_REQUEST)

    def list(self, request) :
        try :
            user = Token.objects.get(key = request.headers.get('Token')).user.id
        except Exception as e:
            print(e)
            return Response({'error_message': "Account doesn't exist. Please try again!"}, status = status.HTTP_401_UNAUTHORIZED)
            
        bookmark = Bookmarks.objects.filter(user = user) 
        serializer = BookmarkSerializer(bookmark, many=True)

        bookmarked_questions = []

        for sd in serializer.data :
            bookmarked_questions.append(Cards.objects.filter(id = sd['bookmark']).values().first())

        return Response(bookmarked_questions)

    def delete(self, request) :
        queryset = Bookmarks.objects.all()
        bookmarks = get_object_or_404(queryset, pk = request.data.get('id'))

        bookmarks.delete()
        return Response({'message': "Bookmark Successfully deleted!"}, status = status.HTTP_200_OK)
