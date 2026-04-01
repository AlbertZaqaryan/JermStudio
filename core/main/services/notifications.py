import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("notifications")


# ─── low-level sender ─────────────────────────────────────────────────

def _send_email_sync(subject, template_name, context, recipient_email):
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        logger.info("Email sent to %s — %s", recipient_email, subject)
    except Exception:
        logger.exception("Email FAILED to %s — %s", recipient_email, subject)


def send_notification_email(subject, template_name, context, recipient_email):
    """Fire-and-forget email via a daemon thread (non-blocking)."""
    thread = threading.Thread(
        target=_send_email_sync,
        args=(subject, template_name, context, recipient_email),
        daemon=True,
    )
    thread.start()


# ─── public notification API ──────────────────────────────────────────

def notify_booking_confirmed(booking):
    send_notification_email(
        subject="Your Booking is Confirmed — Jerm Studio",
        template_name="email/booking_confirmation.html",
        context=_booking_context(booking),
        recipient_email=booking.email,
    )


def notify_booking_updated(booking, old_date, old_time):
    ctx = {
        **_booking_context(booking),
        "old_date": old_date,
        "old_time": old_time,
        "new_date": booking.date,
        "new_time": booking.time,
    }
    send_notification_email(
        subject="Your Booking Has Been Updated — Jerm Studio",
        template_name="email/booking_updated.html",
        context=ctx,
        recipient_email=booking.email,
    )


def notify_booking_canceled(booking):
    send_notification_email(
        subject="Your Booking Has Been Canceled — Jerm Studio",
        template_name="email/booking_canceled.html",
        context=_booking_context(booking),
        recipient_email=booking.email,
    )


# ─── helpers ──────────────────────────────────────────────────────────

def _booking_context(booking):
    return {
        "first_name": booking.first_name,
        "last_name": booking.last_name,
        "email": booking.email,
        "date": booking.date,
        "time": booking.time,
        "studio_name": "Jerm Studio",
        "studio_email": getattr(settings, "DEFAULT_FROM_EMAIL", ""),
    }
