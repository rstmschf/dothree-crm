import uuid
from rest_framework import generics, permissions, status
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer,
    UserMeSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsNotGuest
from rest_framework.response import Response
from django.conf import settings
from sales.services import send_telegram_message
from rest_framework.views import APIView

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class TelegramLinkView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotGuest]

    def get(self, request, *args, **kwargs):
        request.user.telegram_sync_token = uuid.uuid4()
        request.user.save(update_fields=["telegram_sync_token"])

        bot_username = settings.TELEGRAM_BOT_USERNAME
        token = request.user.telegram_sync_token
        link = f"https://t.me/{bot_username}?start={token}"

        return Response(
            {"telegram_link": link, "is_linked": bool(request.user.telegram_chat_id)}
        )


class TelegramWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        message = request.data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if text.startswith("/start ") and chat_id:
            token_str = text.split(" ")[1]

            try:
                user = User.objects.get(telegram_sync_token=token_str)

                user.telegram_chat_id = str(chat_id)
                user.telegram_sync_token = uuid.uuid4()
                user.save(update_fields=["telegram_chat_id", "telegram_sync_token"])

                send_telegram_message(
                    chat_id,
                    f"✅ Account {user.username} connected successfully! Now you may receive notifications here.",
                )

            except (User.DoesNotExist, ValueError):
                send_telegram_message(
                    chat_id,
                    "❌ Wrong link token. Create new and try again.",
                )

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
