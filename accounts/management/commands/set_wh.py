import requests
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Registers the Telegram Webhook securely'

    def add_arguments(self, parser):
        parser.add_argument('base_url', type=str, help='Your public server URL (e.g., https://dothree-crm.com)')

    def handle(self, *args, **options):
        base_url = options['base_url'].rstrip('/') 
        webhook_url = f"{base_url}/api/accounts/telegram/webhook/" 

        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        secret_token = getattr(settings, 'TELEGRAM_WEBHOOK_SECRET', None)

        if not bot_token or not secret_token:
            self.stdout.write(self.style.ERROR(
                "Error: TELEGRAM_BOT_TOKEN or TELEGRAM_WEBHOOK_SECRET is missing in your .env file."
            ))
            return

        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        data = {
            "url": webhook_url,
            "secret_token": secret_token
        }

        try:
            self.stdout.write(f"Connecting to Telegram API...")
            response = requests.post(api_url, data=data)
            result = response.json()

            if result.get('ok'):
                self.stdout.write(self.style.SUCCESS(f"Webhook successfully set to: {webhook_url}"))
                self.stdout.write(self.style.SUCCESS(f"Secret token activated."))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to set webhook: {result.get('description')}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Network error occurred: {str(e)}"))