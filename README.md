# Dothree CRM

A CRM built around a real sales pipeline. The goal was to cover the workflows a sales team actually uses daily.

<img width="1917" height="916" alt="overview" src="https://github.com/user-attachments/assets/ee72e699-65ef-42e3-98bd-bd4b19288d2c" />

### Stack

**Backend:** Python / Django / Django REST Framework  
**Async/Background:** Celery & Celery Beat  
**Frontend:** React / Tailwind CSS / DaisyUI  
**Infrastructure:** Docker (6 containers: Backend, Frontend/Nginx, Postgres, Redis, Celery Worker, Celery Beat)

---

### Features

**Real-time updates**  
Deal and note changes broadcast instantly to all connected clients via WebSockets (Django Channels + Redis). No polling.


https://github.com/user-attachments/assets/cdb9788e-ac8b-457a-a3a7-6bd9364b8127


https://github.com/user-attachments/assets/94cd918c-2553-4f7c-93ca-2a7930f6474b



**AI note formatting**  
Sales reps often leave rough notes mid-call. Enabling trigger on any note and a background Celery task sends it to Groq (openai/gpt-oss-120b) for cleanup. The original text is preserved and accessible. Model is swappable via one config change.


https://github.com/user-attachments/assets/f64e428d-2397-454c-a7d5-815d3dc5dae1


**Telegram alerts**  
Upcoming calls send a Telegram message (harder to miss than a browser tab) directly to the manager. Handled by Celery Beat on a schedule.

<img width="556" height="567" alt="telegram" src="https://github.com/user-attachments/assets/86fb0515-e01a-48aa-811b-4070290125aa" />

**Role-based permissions**  
Three roles: Guest, Sales Rep, Manager. Reps see only their own deals. Managers see everything, including their team's pipelines. Enforced at the API level.

**Soft deletes**  
Uses `django-safedelete` with cascade. Deleted records are hidden from the UI but stay in the database.

**Analytics dashboard**  
Tracks pipeline value, expected revenue, and win rates per rep and overall.

**Auth**  
JWT with access/refresh token rotation.

**Audit logging**  
Deal changes are logged and visible in the Django admin panel.

**API docs**  
Auto-generated Swagger/OpenAPI docs at `/api/docs/`.

---

### Database

[![dbstructure](https://github.com/user-attachments/assets/89294ba7-da28-460a-8041-26a4d924ffb1)](https://dbdiagram.io/d/dbstructure-69af37fdcf54053b6f43b8bd)

---

## Local Setup

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

**1. Clone & configure**
```bash
cp example.env .env
```
Groq API key (free tier works): https://console.groq.com/keys

**2. Build & run**
```bash
docker compose build
docker compose up -d
```

**3. Seed the database**

Run via `docker exec -it crm_web python manage.py <command>`:

| Command | What it does |
|---|---|
| `setup_admin` | Creates admin user (superuser / password) |
| `seed_stages` | Creates 5 sales stages |
| `seed_crm_data` | Generates companies, leads, contacts, deals, and sales users |
| `full` | Runs all three |

**4. Run tests**
```bash
docker exec -it crm_web pytest
```

Covers user models, API access, and permission enforcement.

**5. Access**

| | URL |
|---|---|
| App | `http://localhost` |
| Admin | `http://localhost:8000/admin/` |
| API docs | `http://localhost:8000/api/docs/` |

---

## Telegram Bot Setup

**1.** Install [ngrok](https://ngrok.com/)

**2.** Create a bot via `@BotFather` on Telegram, get the token

**3.** Add to `.env`:
```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_WEBHOOK_SECRET=your_secret
```

**4.** Expose your local server:
```bash
ngrok http 8000
```

**5.** Register the webhook:
```bash
docker exec -it crm_web python manage.py set_wh <YOUR_NGROK_URL>
```
