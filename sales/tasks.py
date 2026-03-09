from celery import shared_task
from .models import Note, Reminder
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from groq import Groq
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .services import send_telegram_message

ai_client = Groq(api_key=settings.AI_API_KEY)


def send_deal_websocket_update(deal_id, note_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"deal_{deal_id}", {"type": "new_comment", "message": note_data}
    )


@shared_task
def broadcast_new_note_task(note_id):
    from .serializers import NoteSerializer

    try:
        note = Note.objects.get(id=note_id)
        note_data = NoteSerializer(note).data
        send_deal_websocket_update(note.deal.id, note_data)
    except Note.DoesNotExist:
        pass


@shared_task
def process_ai_note_task(note_id, prompt_text):
    try:
        note = Note.objects.get(id=note_id)
        system_text = "Make this CRM comment brief and professional, don't add headings or anything, keep all the important info, keep input language"
        chat_completion = ai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": prompt_text},
            ],
            model="openai/gpt-oss-120b",
        )

        ai_formatted_text = chat_completion.choices[0].message.content

        note.text = f"AI Summary:\n{ai_formatted_text}"
        note.save()

        from .serializers import NoteSerializer

        note_data = NoteSerializer(note).data
        send_deal_websocket_update(note.deal.id, note_data)

    except Exception as e:
        note = Note.objects.get(id=note_id)
        note.text = f"❌ API Error: {str(e)}"
        note.save()

        from .serializers import NoteSerializer

        note_data = NoteSerializer(note).data
        send_deal_websocket_update(note.deal.id, note_data)


@shared_task
def check_upcoming_reminders():
    now = timezone.now()
    channel_layer = get_channel_layer()

    time_1h_from_now = now + timedelta(hours=1)
    if Reminder.objects.all().exists():
        reminders_1h = Reminder.objects.filter(
            is_done=False, reminded_1h=False, date__lte=time_1h_from_now, date__gt=now
        )

        for r in reminders_1h:
            if r.owner:
                async_to_sync(channel_layer.group_send)(
                    f"user_{r.owner.id}",
                    {
                        "type": "send_notification",
                        "notification_type": "reminder_alert",
                        "message": {
                            "title": "Event soon!",
                            "text": f"In 1 hour: {r.text} (Deal: {r.deal.title})",
                            "deal_id": r.deal.id,
                            "urgency": "warning",
                        },
                    },
                )
                if r.owner.telegram_chat_id:
                    msg = (
                        f"🔔 Reminder!\n\n"
                        f"💼 Deal: {r.deal.title}\n"
                        f"📝 Task: {r.text}\n"
                        f"⏰ Time: {r.date.strftime('%H:%M')}"
                    )
                    send_telegram_message(r.owner.telegram_chat_id, msg)
            r.reminded_1h = True
            r.save(update_fields=["reminded_1h"])

        time_5m_from_now = now + timedelta(minutes=5)
        reminders_5m = Reminder.objects.filter(
            is_done=False, reminded_5m=False, date__lte=time_5m_from_now, date__gt=now
        )

        for r in reminders_5m:
            if r.owner:
                async_to_sync(channel_layer.group_send)(
                    f"user_{r.owner.id}",
                    {
                        "type": "send_notification",
                        "notification_type": "reminder_alert",
                        "message": {
                            "title": "Event soon!",
                            "text": f"In 5 minutes: {r.text}",
                            "deal_id": r.deal.id,
                            "urgency": "danger",
                        },
                    },
                )
                if r.owner.telegram_chat_id:
                    msg = (
                        f"🔔 Reminder!\n\n"
                        f"💼 Deal: {r.deal.title}\n"
                        f"📝 Task: {r.text}\n"
                        f"⏰ Time: {r.date.strftime('%H:%M')}"
                    )
                    send_telegram_message(r.owner.telegram_chat_id, msg)
            r.reminded_5m = True
            r.save(update_fields=["reminded_5m"])


@shared_task
def broadcast_reminder_update(reminder_id, owner_id, action="updated"):
    from .models import Reminder
    from .serializers import ReminderSerializer

    channel_layer = get_channel_layer()

    def send_payload(payload):
        if owner_id:
            async_to_sync(channel_layer.group_send)(f"user_{owner_id}", payload)
        async_to_sync(channel_layer.group_send)("management_group", payload)

    if action == "deleted":
        send_payload(
            {
                "type": "send_notification",
                "notification_type": "reminder_deleted",
                "message": {"id": reminder_id},
            }
        )
        return

    try:
        reminder = Reminder.objects.get(id=reminder_id)
        data = ReminderSerializer(reminder).data
        send_payload(
            {
                "type": "send_notification",
                "notification_type": f"reminder_{action}",
                "message": data,
            }
        )
    except Reminder.DoesNotExist:
        pass
