from celery import shared_task
from .models import Note, Reminder
from groq import Groq
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

ai_client = Groq(api_key=settings.AI_API_KEY)


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

        note.text = f"AI Summary:{ai_formatted_text}"
        note.save()

    except Exception as e:
        raise ValidationError(f"❌ API Error: {str(e)}")
    


@shared_task
def check_upcoming_reminders():

    now = timezone.now()
    time_1h_from_now = now + timedelta(hours=1)
    
    reminders_1h = Reminder.objects.filter(
        is_done=False,
        reminded_1h=False,
        date__lte=time_1h_from_now,
        date__gt=now
    )
    
    for r in reminders_1h:
        print(f"🔔 1 hour before '{r.text}' for {r.deal.title}")
        
        r.reminded_1h = True
        r.save(update_fields=['reminded_1h'])


    time_5m_from_now = now + timedelta(minutes=5)
    
    reminders_5m = Reminder.objects.filter(
        is_done=False,
        reminded_5m=False,
        date__lte=time_5m_from_now,
        date__gt=now
    )
    
    for r in reminders_5m:
        print(f"🚨 5 minutes before '{r.text}' for {r.deal.title}")
        
        r.reminded_5m = True
        r.save(update_fields=['reminded_5m'])
