import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.views.generic import RedirectView
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .models import Event
from .serializers import EventSerializer, UserSerializer
import requests
class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, есть ли токен в куках запроса
        jwt_token = request.COOKIES.get('jwt_token')
        print(jwt_token)
        # Если токен присутствует, пытаемся аутентифицировать пользователя
        if jwt_token:
            try:
                # Декодируем токен и находим пользователя
                user_id = decode_jwt_token(jwt_token)
                user = User.objects.get(id=user_id)

                # Аутентифицируем пользователя
                request.user = user
            except:
                # Если произошла ошибка при декодировании токена или поиске пользователя, игнорируем его
                pass

        response = self.get_response(request)

        return response

def decode_jwt_token(token):
    try:
        # Декодируем токен, используя секретный ключ, заданный в настройках Django
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        # Получаем идентификатор пользователя из декодированного токена
        user_id = decoded_payload.get('user_id')
        return user_id
    except jwt.ExpiredSignatureError:
        # Если токен истек, выбрасываем ошибку
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError:
        # Если токен недействителен, выбрасываем ошибку
        raise ValueError('Invalid token')


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()

        # Получаем JWT токен из куки
        jwt_token = request.COOKIES.get('jwt_token')
        print(request.user)
        if jwt_token:
            try:
                # Декодируем токен, чтобы получить идентификатор пользователя
                decoded_payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_payload.get('user_id')

                # Получаем пользователя по его идентификатору
                user = User.objects.get(id=user_id)

                if user in event.registered_users.all():
                    return render(request, 'event/login.html')

                event.registered_users.add(user)
                refresh = RefreshToken.for_user(user)

                return JsonResponse({
                    "user_id": user.id,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token has expired"}, status=400)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token"}, status=400)
        else:
            return JsonResponse({"error": "JWT token is missing"}, status=400)

    @method_decorator(ensure_csrf_cookie)  # Добавляем декоратор, чтобы убедиться, что CSRF-токен включен в ответ
    @action(detail=True, methods=['post'])
    def cancel_registration(self, request, pk):
        event = self.get_object()
        # Получаем JWT токен из куки
        jwt_token = request.COOKIES.get('jwt_token')
        if jwt_token:
            try:
                # Декодируем токен, чтобы получить идентификатор пользователя
                decoded_payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_payload.get('user_id')

                # Получаем пользователя по его идентификатору
                user = User.objects.get(id=user_id)

                event.registered_users.remove(user)
                refresh = RefreshToken.for_user(user)

                return redirect('/my_events/')
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token has expired"}, status=400)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token"}, status=400)
        else:
            return JsonResponse({"error": "JWT token is missing"}, status=400)


class CreateUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        form = UserCreationForm()
        return render(request, 'event/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)

            # Создание JWT токена для нового пользователя
            refresh = RefreshToken.for_user(user)

            # Устанавливаем токен в куках ответа
            response = JsonResponse({
                "user_id": user.id,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)

            # Устанавливаем JWT токен в куки
            response = redirect('/')
            response.set_cookie('jwt_token', str(refresh.access_token), httponly=True)

            return response
        else:
            # Если форма невалидна, передаем ее обратно в шаблон для отображения ошибок
            return render(request, 'event/register.html', {'form': form})

class CustomTokenObtainPairView(TokenObtainPairView):
    @method_decorator(ensure_csrf_cookie)  # Ensure CSRF cookie is set in the response
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @method_decorator(csrf_protect)  # Apply CSRF protection to the view
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Если аутентификация успешна, сохраняем токен в localStorage
            token = response.data.get('access')
            if token:
                request.session['jwt_token'] = token
        return response


class TokenRefreshCustomView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = self.get_token(serializer)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

def events(request):
    return render(request, 'event/events.html')

# Обработка отсутствия токена

def event_api(request):
    events = Event.objects.all()
    data = [{'id': event.id,
             'title': event.title,
             'description': event.description,
             'start_date': event.start_date.strftime('%Y-%m-%d %H:%M:%S'),
             'end_date': event.end_date.strftime('%Y-%m-%d %H:%M:%S'),
             'location': event.location,
             'registered_users': list(event.registered_users.values_list('id', flat=True)),
             } for event in events]
    return JsonResponse(data, safe=False)




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Создаем токен доступа
            token_request_data = {'username': user.username, 'password': request.POST['password']}
            token_response = CustomTokenObtainPairView.as_view()(request, data=token_request_data)
            # Перенаправляем на страницу с мероприятиями и сохраняем токен в куках
            if token_response.status_code == 200:
                response = redirect('events')
                token = token_response.data.get('access')
                if token:
                    response.set_cookie('jwt_token', token, httponly=True)  # Сохраняем токен в куках
                return response
    else:
        form = AuthenticationForm()
    return render(request, 'event/login.html', {'form': form})


class CustomLogoutView(RedirectView):
    pattern_name = 'events'  # Перенаправление на страницу входа после выхода из системы

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)

def my_events(request):
    if request.user.is_authenticated:
        user = request.user
        # Получаем queryset мероприятий, на которые пользователь зарегистрирован
        registred_events = Event.objects.filter(registered_users=user.id)

        # Преобразуем queryset в список
        registred_events_list = list(registred_events)
        print(registred_events_list)
        # Передаем список мероприятий в контекст шаблона
        return render(request, 'event/my_events.html', {'registered_events': registred_events_list})
    else:
        # Если пользователь не аутентифицирован, перенаправляем его на страницу входа
        return redirect('login')