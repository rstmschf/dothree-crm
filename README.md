# Dothree CRM

A CRM built around a real sales pipeline. The goal was to cover the workflows a sales team actually uses daily.

### Stack

**Backend:** Python / Django / Django REST Framework  
**Async/Background:** Celery & Celery Beat  
**Frontend:** React / Tailwind CSS / DaisyUI  
**Infrastructure:** Docker (6 containers: Backend, Frontend/Nginx, Postgres, Redis, Celery Worker, Celery Beat)

---

### Features

**Real-time updates**  
Deal and note changes broadcast instantly to all connected clients via WebSockets (Django Channels + Redis). No polling.

**AI note formatting**  
Sales reps often leave rough notes mid-call. Enabling trigger on any note and a background Celery task sends it to Groq (openai/gpt-oss-120b) for cleanup. The original text is preserved and accessible. Model is swappable via one config change.

**Telegram alerts**  
Upcoming calls send a Telegram message (harder to miss than a browser tab) directly to the manager. Handled by Celery Beat on a schedule.

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