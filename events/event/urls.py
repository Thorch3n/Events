from django.urls import path

from .views import CreateUserView, TokenRefreshCustomView, events, event_api, login_view, CustomLogoutView, \
    EventViewSet, CustomTokenObtainPairView, my_events

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='register'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshCustomView.as_view(), name='token_refresh'),
    path('', events, name='events'),
    path('api/events/', event_api, name='events-list'),
    path('api/events/<int:pk>/register/', EventViewSet.as_view({'post': 'register'}), name='register'),
    path('api/events/<int:pk>/cancel_registration/', EventViewSet.as_view({'post': 'cancel_registration'}), name='cancel_registration'),
    path('login/', login_view, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('my_events/', my_events, name='my_events'),
]