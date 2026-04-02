# JERM STUDIO

A production-ready **Django** web application for **Jerm Studio** — a kids photography studio based in Armenia. The platform features an online room showcase, a real-time booking system with automatic email notifications, and a fully translatable admin-managed CMS.

**Live:** [jermstudio.am](https://jermstudio.am)

---

## Features

### Public Website
- **Hero landing page** with studio branding, background imagery, and call-to-action
- **Room gallery** — browse available studio rooms with photos, descriptions, and pricing
- **Place section** — photo gallery showcasing real studio sessions
- **Real-time booking system** — select a date, pick an available time slot, and confirm a session in three steps
- **Multi-language support** — English, Armenian, and Russian with session/cookie-based language switching

### Booking System
- **Hourly time slots** from 09:00 to 21:00 with automatic availability calculation
- **Conflict prevention** via database-level unique constraints (no double bookings)
- **Date/slot APIs** — JSON endpoints for dynamic calendar and time picker on the frontend
- **Status tracking** — bookings have `booked` / `canceled` states
- **Phone number validation** with regex-based validator

### Email Notifications (via Django Signals)
- **Booking confirmed** — customer receives an HTML email with date and time details
- **Booking updated** — email sent automatically when an admin changes the date or time
- **Booking canceled** — email sent when a booking is deleted or canceled from the admin panel
- Powered by **Gmail SMTP** with credentials loaded from environment variables
- Professional **HTML email templates** with Jerm Studio branding

### Admin Panel
- Full CRUD for **Rooms**, **Bookings**, **Place Photos**, and **Site Content**
- **Bulk cancel action** — select multiple bookings and cancel them with one click (triggers notification emails)
- **CMS-style Site Content** — edit every heading, button label, placeholder, and message per language directly from the admin
- **Site Settings** — configure the global font family

---

## Tech Stack

| Layer        | Technology                               |
|:-------------|:-----------------------------------------|
| Backend      | Python 3, Django 5.2                     |
| Frontend     | Tailwind CSS (CDN), vanilla JavaScript   |
| Database     | SQLite (default), any Django-supported DB|
| Static files | WhiteNoise                               |
| Email        | Django `send_mail` / Gmail SMTP          |
| Deployment   | Phusion Passenger (shared hosting)       |

---

## Project Structure

```
core/                         # Django project root (manage.py lives here)
├── manage.py
├── requirements.txt
├── .env                      # Environment variables (not committed)
├── passenger_wsgi.py         # Shared-hosting WSGI entry point
│
├── core/                     # Django project package
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
│   ├── celery.py             # Celery app (optional async)
│   └── __init__.py
│
├── main/                     # Primary application
│   ├── models.py             # Room, Booking, SiteContent, SiteSettings, PlacePhoto
│   ├── views.py              # Landing page + JSON booking APIs
│   ├── urls.py               # Route definitions
│   ├── admin.py              # Admin configuration with custom actions
│   ├── signals.py            # post_save / pre_delete → email notifications
│   ├── apps.py               # AppConfig with signal registration
│   ├── context_processors.py # Injects SiteSettings into templates
│   ├── tasks.py              # Celery tasks (optional)
│   ├── services/
│   │   └── notifications.py  # Email notification service
│   ├── static/main/
│   │   ├── css/styles.css
│   │   └── js/main.js
│   └── migrations/
│
└── templates/
    ├── base.html
    ├── main/index.html
    ├── main/components/room_card.html
    └── email/
        ├── booking_confirmation.html
        ├── booking_updated.html
        └── booking_canceled.html
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/JermStudio.git
cd JermStudio/core

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the `core/` directory:

```env
SECRET_KEY=your-django-secret-key

# Gmail SMTP
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
```

> **Gmail App Password:** Go to [Google Account → Security → App Passwords](https://myaccount.google.com/apppasswords) and generate one for "Mail".

### Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Run the Development Server

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) for the site and [http://localhost:8000/admin/](http://localhost:8000/admin/) for the admin panel.

---

## API Endpoints

| Method | Endpoint               | Description                           |
|:-------|:-----------------------|:--------------------------------------|
| GET    | `/api/available-dates/`| Returns available booking dates       |
| GET    | `/api/available-slots/?date=YYYY-MM-DD` | Returns open time slots for a date |
| POST   | `/api/bookings/`       | Creates a new booking                 |

### Create Booking — request body

```json
{
  "first_name": "Anna",
  "last_name": "Hovhannisyan",
  "email": "anna@example.com",
  "phone": "+37498123456",
  "date": "2026-04-15",
  "time": "14:00"
}
```

---

## Email Notifications

Notifications are triggered automatically via **Django signals** — no manual calls needed:

| Event                     | Trigger                                    | Email sent to     |
|:--------------------------|:-------------------------------------------|:------------------|
| Booking created           | `post_save` with `created=True`            | Customer's email  |
| Date or time changed      | `post_save` with date/time field change    | Customer's email  |
| Booking canceled (admin)  | Status set to `canceled` or record deleted | Customer's email  |

Each email uses a branded HTML template with the studio logo and warm color palette.

---

## Celery (Optional Async)

For high-traffic scenarios, email sending can be offloaded to Celery workers:

```bash
# Install Redis, then:
pip install celery redis

# Start the worker
celery -A core worker --loglevel=info
```

The Celery tasks in `main/tasks.py` include automatic retry logic (3 retries, 60-second delay).

---

## Deployment

The project includes a `passenger_wsgi.py` for **Phusion Passenger** shared hosting. Static files are served by **WhiteNoise**.

```bash
# Collect static files before deploying
python manage.py collectstatic --noinput
```

---

## License

This project is proprietary software for Jerm Studio. All rights reserved.
