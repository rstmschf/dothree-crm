import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from sales.models import Stage, Deal, Note
from clients.models import Company

@pytest.fixture
def setup_deal_data(user):
    company = Company.objects.create(name="Test Co", owner=user)
    stage = Stage.objects.create(name="New", order=1)
    deal = Deal.objects.create(
        title="Test Deal", 
        value=1000, 
        company=company, 
        stage=stage, 
        owner=user,
        created_by=user
    )
    return deal

@pytest.mark.django_db
class TestNoteAPI:

    def test_create_normal_note(self, auth_api_client, setup_deal_data, user):
        url = reverse("note-list")
        payload = {
            "deal": setup_deal_data.id,
            "text": "Call client tomorrow."
        }
        
        with patch("sales.tasks.broadcast_new_note_task.delay") as mock_ws_task:
            response = auth_api_client.post(url, payload, format="json")
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["text"] == "Call client tomorrow."
            mock_ws_task.assert_called_once_with(response.data["id"])

    def test_create_ai_note_triggers_celery(self, auth_api_client, setup_deal_data, user):
        url = reverse("note-list")
        payload = {
            "deal": setup_deal_data.id,
            "text": "@bot summarize this deal"
        }

        with patch("sales.tasks.process_ai_note_task.delay") as mock_ai_task, \
             patch("sales.tasks.broadcast_new_note_task.delay") as mock_ws_task:
            
            response = auth_api_client.post(url, payload, format="json")
            
            assert response.status_code == status.HTTP_201_CREATED
            assert "⏳" in response.data["text"] 
            assert response.data["original_text"] == "@bot summarize this deal"
            
            note_id = response.data["id"]
            

            mock_ai_task.assert_called_once()
            mock_ws_task.assert_called_once_with(note_id)

    def test_cannot_add_note_to_others_deal(self, api_client, setup_deal_data, django_user_model):
        other_user = django_user_model.objects.create_user(
            username="other", password="pw", role="sales"
        )
        url = reverse("login")
        r = api_client.post(url, {"username": "other", "password": "pw"}, format="json")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")

        note_url = reverse("note-list")
        payload = {
            "deal": setup_deal_data.id,
            "text": "Sneaking into your deal."
        }
        
        response = api_client.post(note_url, payload, format="json")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN