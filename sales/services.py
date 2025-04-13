from .models import Deal, Stage, ActivityLog
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.conf import settings
from groq import Groq


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


client = Groq(api_key=settings.AI_API_KEY)


def format_manager_note_with_ai(raw_text):
    """Отправляет текст иишке и возвращает отформатированный вариант"""
    system_text = "Make this CRM comment brief and professional, don't add headings or anything, keep all the important info, keep input language"
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": raw_text},
            ],
            model="openai/gpt-oss-120b",
        )
        return response.choices[0].message.content
    except Exception as e:
        raise e
