# Dothree CRM

A full-stack CRM built to handle the actual chaos of a real-world sales pipeline. Powered by Django, React, and practical automation, this tool is designed around the daily workflows of sales reps and managers to stop losing important deals.

### Key Features

* **Real-Time Everything:** Powered by WebSockets (Django Channels + Redis). When a deal moves or a note is added, the UI updates instantly for everyone.
* **The "AI Secretary":** Integrated with Groq (openai/gpt-oss-120b, easily swappable for any API). If you’re in a rush and leave a messy note, just tag `@bot`. The AI automatically grabs it and formats it into clean, professional text.
* **Proactive Telegram Alerts:** Connected to a backend bot. If a manager has a call coming up, they get a ping directly on Telegram. Active reminders are also handled in the React UI via `celery-beat`, but a Telegram ping is much harder to ignore than a browser tab.
* **Role-Based Access Control:** Custom permissions. Guests are guests, Reps see their own pipelines, and Managers have full visibility over their data and their subordinates' data.
* **Soft Deletes:** Implemented `django-safedelete`. "Deleted" deals are safely hidden from the UI, not wiped from the database.
* **Business Analytics:** Custom dashboards tracking pipeline value, expected revenue, and win rates.

### Inside

* **Authentication:** Secure, stateless JWT auth with access/refresh token rotation.
* **Background Tasks:** The AI Secretary and Telegram/UI alerts run in the background (Celery, Celery Beat, Redis) so the main server never slows down.
* **Audit Logging:** Simple, built-in tracking for deal changes, accessible via the Django admin panel.
* **Self-Documenting API:** Automatic Swagger/OpenAPI docs generation (accessible at `/api/docs/`).
* **Infrastructure:** Multi-staged Docker builds with health checks and clean dependency management.

### Stack

* **Backend:** Python 3.13 / Django 6 / Django REST Framework
* **Async/Background:** Celery & Celery Beat
* **Frontend:** Simple React / Tailwind CSS / DaisyUI
* **Infrastructure:** Fully Dockerized (6 containers: Backend, Frontend/Nginx, Postgres, Redis, Celery Worker, Celery Beat)

---

## Local Development

**Prerequisites:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

**1. Clone & Configure**
Clone the repository and create your environment variables:
```bash
cp example.env .env
```
If you don't have API Key, you can create it here: https://console.groq.com/keys

**2. Build & Run**
```bash
docker compose build
docker compose up -d
```

**3. Database Setup & Seeding**
Use the custom management commands to populate the CRM with test data. Run these via `docker exec -it crm_web python manage.py <command>`:

* `setup_admin`: Creates an admin user (Username: *superuser*, Password: *password*).
* `seed_stages`: Creates 5 standard sales stages (New, Qualification, Negotiation, Closed Won, Closed Lost).
* `seed_crm_data`: Generates random companies, leads, contacts, deals, and "Sales" users to test permissions.
* **`full`**: Runs all three commands above to completely set up a test environment in one go.

**4. Run Tests**
To verify user models, API accessibility, and permissions:
```bash
docker exec -it crm_web pytest
```

**5. Access the App**
* **CRM Application:** `http://localhost`
* **Admin Panel:** `http://localhost:8000/admin/`
* **API Documentation:** `http://localhost:8000/api/docs/`

---

## Setting up the Telegram Bot

To test the real-time Telegram alerts locally, you need a test bot. The setup is fully automated via a custom management command.

1.  **Get a Tool for Local Webhooks:** Install [ngrok](https://ngrok.com/).
2.  **Create a Bot:** Open Telegram, message `@BotFather`, and send `/newbot`. Follow the steps to get your HTTP API Token.
3.  **Update `.env`:** Add your token and invent a secret string to secure your webhook:
    ```env
    TELEGRAM_BOT_TOKEN=your_token_from_botfather
    TELEGRAM_WEBHOOK_SECRET=MySuperSecret123
    ```
4.  **Expose your Local Server:** Run ngrok to get a public HTTPS URL:
    ```bash
    ngrok http 8000
    ```
5.  **Register the Webhook:** Copy the `https://` link provided by ngrok and run this command:
    ```bash
    docker exec -it crm_web python manage.py set_webhook <YOUR_NGROK_URL>
    ```