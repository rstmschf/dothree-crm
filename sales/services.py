from .models import Deal, Stage, ActivityLog
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.conf import settings
import requests


def move_deal_to_stage(deal: Deal, stage: Stage, actor=None, message: str = "") -> Deal:
    old_stage = deal.stage
    if old_stage == stage:
        return deal

    deal.stage = stage
    deal.save(update_fields=["stage", "updated_at"])

    ActivityLog.objects.create(
        actor=actor,
        verb="moved_stage",
        message=f"Stage changed: {old_stage} -> {stage}. {message}",
        content_type=ContentType.objects.get_for_model(deal),
        object_id=deal.pk,
    )

    if stage.is_won and deal.close_date is None:
        deal.close_date = timezone.now()
        deal.save(update_fields=["close_date"])
        ActivityLog.objects.create(
            actor=actor,
            verb="won",
            message=f"Deal marked as WON at stage {stage}.",
            content_type=ContentType.objects.get_for_model(deal),
            object_id=deal.pk,
        )

    if stage.is_lost:
        ActivityLog.objects.create(
            actor=actor,
            verb="lost",
            message=f"Deal marked as LOST at stage {stage}.",
            content_type=ContentType.objects.get_for_model(deal),
            object_id=deal.pk,
        )

    return deal


def send_telegram_message(chat_id, text):
    if not chat_id:
        return
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
    except requests.RequestException as e:
        print(f"Telegram API Error: {e}")
