"""
Celery tasks for async email notifications.

To use Celery instead of threading:
  1. Install Redis and start it.
  2. pip install celery redis
  3. Set CELERY_BROKER_URL in .env
  4. Run:  celery -A core worker --loglevel=info
  5. In services/notifications.py, replace the threading calls
     with the .delay() calls shown below.

Example swap in notifications.py:
    from main.tasks import send_email_task
    send_email_task.delay(subject, template, context, recipient)
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("notifications")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, subject, template_name, context, recipient_email):
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
    except Exception as exc:
        logger.exception("Email FAILED to %s — %s", recipient_email, subject)
        raise self.retry(exc=exc)
