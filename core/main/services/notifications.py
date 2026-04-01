import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("notifications")


# ─── low-level senders ────────────────────────────────────────────────

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


def send_sms(to_number, body):
    """Send an SMS via Twilio.  Silently skips if Twilio is not configured."""
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_number = getattr(settings, "TWILIO_PHONE_NUMBER", None)

    if not all([account_sid, auth_token, from_number]):
        logger.debug("Twilio not configured — skipping SMS to %s", to_number)
        return

    def _send():
        try:
            from twilio.rest import Client  # noqa: delay import
            client = Client(account_sid, auth_token)
            client.messages.create(body=body, from_=from_number, to=to_number)
            logger.info("SMS sent to %s", to_number)
        except Exception:
            logger.exception("SMS FAILED to %s", to_number)

    threading.Thread(target=_send, daemon=True).start()


# ─── public notification API ──────────────────────────────────────────

def notify_booking_confirmed(booking):
    ctx = _booking_context(booking)
    send_notification_email(
        subject="Your Booking is Confirmed — Jerm Studio",
        template_name="email/booking_confirmation.html",
        context=ctx,
        recipient_email=booking.email,
    )
    send_sms(
        booking.phone,
        f"Hi {booking.first_name}! Your booking at Jerm Studio is confirmed "
        f"for {booking.date.strftime('%B %d, %Y')} at {booking.time.strftime('%H:%M')}.",
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
    send_sms(
        booking.phone,
        f"Hi {booking.first_name}, your Jerm Studio booking has been updated to "
        f"{booking.date.strftime('%B %d, %Y')} at {booking.time.strftime('%H:%M')}.",
    )


def notify_booking_canceled(booking):
    ctx = _booking_context(booking)
    send_notification_email(
        subject="Your Booking Has Been Canceled — Jerm Studio",
        template_name="email/booking_canceled.html",
        context=ctx,
        recipient_email=booking.email,
    )
    send_sms(
        booking.phone,
        f"Hi {booking.first_name}, your Jerm Studio booking on "
        f"{booking.date.strftime('%B %d, %Y')} at {booking.time.strftime('%H:%M')} "
        f"has been canceled. Contact us with any questions.",
    )


# ─── helpers ──────────────────────────────────────────────────────────

def _booking_context(booking):
    return {
        "first_name": booking.first_name,
        "last_name": booking.last_name,
        "email": booking.email,
        "phone": booking.phone,
        "date": booking.date,
        "time": booking.time,
        "studio_name": "Jerm Studio",
        "studio_email": getattr(settings, "DEFAULT_FROM_EMAIL", ""),
    }
