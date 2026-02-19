from django.urls import reverse
from clients.models import Company
import pytest


@pytest.mark.django_db
def test_create_company(auth_api_client, user):
    url = reverse("company-list")
    payload = {
        "name": "Company for Test LTD",
        "website": "https://test.test",
        "industry": "Test Industry",
    }
    r = auth_api_client.post(url, payload, format="json")
    assert r.status_code == 201
    assert r.data["name"] == "Company for Test LTD"
    obj = Company.objects.get(pk=r.data["id"])
    assert obj.owner == user


@pytest.mark.django_db
def test_list_and_retrieve(auth_api_client, user):
    c1 = Company.objects.create(name="Comp1", owner=user)
    c2 = Company.objects.create(name="Comp2", owner=user)

    list_url = reverse("company-list")
    r = auth_api_client.get(list_url)
    assert r.status_code == 200
    assert any(item["id"] == c1.id for item in r.data)
    assert any(item["id"] == c2.id for item in r.data)

    detail_url = reverse("company-detail", args=[c1.id])
    r2 = auth_api_client.get(detail_url)
    assert r2.status_code == 200
    assert r2.data["name"] == "Comp1"

    detail_url = reverse("company-detail", args=[c2.id])
    r2 = auth_api_client.get(detail_url)
    assert r2.status_code == 200
    assert r2.data["name"] == "Comp2"
