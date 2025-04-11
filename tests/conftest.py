import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword",
        role="admin",
    )


@pytest.fixture
def auth_api_client(api_client, user):
    login_url = reverse("login")
    resp = api_client.post(
        login_url,
        {"username": user.username, "password": "testpassword"},
        format="json",
    )
    assert resp.status_code == 200, (
        "Login fixture failed — check accounts.login endpoint"
    )
    token = resp.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client
