import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from sales.models import Stage, Deal, Reminder
from clients.models import Company

@pytest.fixture
def setup_reminder_data(user):
    company = Company.objects.create(name="Test Co", owner=user)
    stage = Stage.objects.create(name="New", order=1)
    deal = Deal.objects.create(title="Deal", value=100, company=company, stage=stage, owner=user)
    return deal

@pytest.mark.django_db
class TestReminderAPI:

    def test_create_reminder(self, auth_api_client, setup_reminder_data, user):
        url = reverse("reminder-list")
        future_date = timezone.now() + timedelta(days=1)
        
        payload = {
            "text": "Follow up call",
            "deal": setup_reminder_data.id,
            "date": future_date.isoformat()
        }

        with patch("sales.tasks.broadcast_reminder_update.delay") as mock_ws_task:
            response = auth_api_client.post(url, payload, format="json")
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["text"] == "Follow up call"
            assert response.data["is_done"] is False
            assert response.data["owner"] == user.id
            
            mock_ws_task.assert_called_once_with(response.data["id"], user.id, "created")

    def test_toggle_reminder(self, auth_api_client, setup_reminder_data, user):
        reminder = Reminder.objects.create(
            text="Toggle me", 
            deal=setup_reminder_data, 
            date=timezone.now(),
            owner=user
        )
        assert reminder.is_done is False

        url = reverse("reminder-toggle", kwargs={"pk": reminder.pk})

        with patch("sales.tasks.broadcast_reminder_update.delay") as mock_ws_task:
            response = auth_api_client.post(url, format="json")
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data["is_done"] is True
            assert response.data["status"] == "success"
            
            reminder.refresh_from_db()
            assert reminder.is_done is True
            
            mock_ws_task.assert_called_once_with(reminder.id, user.id, "updated")