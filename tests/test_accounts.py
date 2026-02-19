import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_register(api_client):
    url = reverse("register")
    payload = {
        "username": "usertest",
        "email": "mailtest@example.com",
        "password": "passtest",
        "role": "sales",
    }
    r = api_client.post(url, payload, format="json")
    assert r.status_code == 201
    assert r.data["username"] == "usertest"
    assert r.data["email"] == "mailtest@example.com"
    assert "password" not in r.data

@pytest.mark.django_db
def test_login_and_me(api_client):
    user = User.objects.create_user(
        username="loginuser",
        email="login@example.com",
        password="passw0rd",
        role="sales",
    )

    login_url = reverse("login")
    r = api_client.post(
        login_url, {"username": "loginuser", "password": "passw0rd"}, format="json"
    )
    assert r.status_code == 200
    assert "access" in r.data and "refresh" in r.data

    token = r.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    me_url = reverse("me")
    r2 = api_client.get(me_url)
    assert r2.status_code == 200
    assert r2.data["email"] == "login@example.com"
    assert r2.data["username"] == "loginuser"
