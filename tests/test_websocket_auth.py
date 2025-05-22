import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import path
from sales.consumers import NotificationConsumer, DealConsumer
from accounts.middleware import JWTAuthMiddleware, get_user_from_token

User = get_user_model()


def make_application():
    return JWTAuthMiddleware(
        URLRouter([
            path("ws/notifications/", NotificationConsumer.as_asgi()),
            path("ws/deals/<int:deal_id>/", DealConsumer.as_asgi()),
        ])
    )


@pytest.fixture
def ws_user(db):
    return User.objects.create_user(
        username="ws_user",
        email="ws@example.com",
        password="testpassword",
        role="sales",
    )


@pytest.fixture
def valid_token(ws_user):
    return str(AccessToken.for_user(ws_user))


# --- get_user_from_token unit tests ---


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_valid_token_returns_user(ws_user, valid_token):
    user = await get_user_from_token(valid_token)
    assert user.id == ws_user.id
    assert user.username == "ws_user"


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_invalid_token_returns_anonymous():
    user = await get_user_from_token("garbage.token.value")
    assert isinstance(user, AnonymousUser)


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_empty_token_returns_anonymous():
    user = await get_user_from_token("")
    assert isinstance(user, AnonymousUser)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_token_for_deleted_user(ws_user, valid_token):
    await sync_to_async(ws_user.delete)()
    user = await get_user_from_token(valid_token)
    # User.delete() sets is_active=False but doesn't remove the row,
    # so the token still resolves to the user object.
    assert user.id == ws_user.id


# --- Notification WebSocket connection tests ---


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_notification_ws_connects_with_valid_token(valid_token):
    app = make_application()
    communicator = WebsocketCommunicator(app, f"/ws/notifications/?token={valid_token}")
    connected, _ = await communicator.connect()
    assert connected is True
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_notification_ws_rejects_without_token():
    app = make_application()
    communicator = WebsocketCommunicator(app, "/ws/notifications/")
    connected, _ = await communicator.connect()
    assert connected is False
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_notification_ws_rejects_invalid_token():
    app = make_application()
    communicator = WebsocketCommunicator(app, "/ws/notifications/?token=bad.token.here")
    connected, _ = await communicator.connect()
    assert connected is False
    await communicator.disconnect()


# --- Deal WebSocket connection tests ---


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_deal_ws_connects_with_valid_token(valid_token):
    app = make_application()
    communicator = WebsocketCommunicator(app, f"/ws/deals/1/?token={valid_token}")
    connected, _ = await communicator.connect()
    assert connected is True
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_deal_ws_rejects_without_token():
    app = make_application()
    communicator = WebsocketCommunicator(app, "/ws/deals/1/")
    connected, _ = await communicator.connect()
    assert connected is False
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_deal_ws_rejects_invalid_token():
    app = make_application()
    communicator = WebsocketCommunicator(app, "/ws/deals/1/?token=invalid")
    connected, _ = await communicator.connect()
    assert connected is False
    await communicator.disconnect()
