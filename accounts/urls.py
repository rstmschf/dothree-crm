from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, MeView, CustomTokenObtainPairView, TelegramLinkView, TelegramWebhookView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("telegram/link/", TelegramLinkView.as_view(), name="telegram-link"),
    path("telegram/webhook/", TelegramWebhookView.as_view(), name="telegram-wh")
]   
