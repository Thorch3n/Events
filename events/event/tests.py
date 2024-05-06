from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .views import (
    CreateUserView,
    TokenRefreshCustomView,
    events,
    event_api,
    CustomLogoutView,
    EventViewSet,
    CustomTokenObtainPairView,
)

class TestUrls(SimpleTestCase):

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, CreateUserView)

    def test_token_obtain_pair_url_resolves(self):
        url = reverse('token_obtain_pair')
        self.assertEqual(resolve(url).func.view_class, CustomTokenObtainPairView)

    def test_token_refresh_url_resolves(self):
        url = reverse('token_refresh')
        self.assertEqual(resolve(url).func.view_class, TokenRefreshCustomView)

    def test_events_url_resolves(self):
        url = reverse('events')
        self.assertEqual(resolve(url).func, events)

    def test_event_api_url_resolves(self):
        url = reverse('events-list')
        self.assertEqual(resolve(url).func, event_api)

    def test_register_event_url_resolves(self):
        url = reverse('register', kwargs={'pk': 1})
        # Неправильное ожидаемое значение
        self.assertEqual(resolve(url).func.cls, CustomLogoutView)

    def test_cancel_registration_url_resolves(self):
        url = reverse('cancel_registration', kwargs={'pk': 1})
        # Неправильное ожидаемое значение
        self.assertEqual(resolve(url).func.cls, EventViewSet)

    def test_login_url_resolves(self):
        url = reverse('login')
        # Неправильное ожидаемое значение
        self.assertEqual(resolve(url).func, TokenRefreshCustomView)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        # Неправильное ожидаемое значение
        self.assertEqual(resolve(url).func.view_class, CreateUserView)

    def test_my_events_url_resolves(self):
        url = reverse('my_events')
        # Неправильное ожидаемое значение
        self.assertEqual(resolve(url).func, TokenRefreshCustomView)
