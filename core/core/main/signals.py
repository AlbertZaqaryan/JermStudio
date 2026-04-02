import logging

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Booking
from .services.notifications import (
    notify_booking_canceled,
    notify_booking_confirmed,
    notify_booking_updated,
)

logger = logging.getLogger("notifications")


@receiver(post_save, sender=Booking)
def booking_post_save(sender, instance, created, **kwargs):
    if created:
        notify_booking_confirmed(instance)
        return

    old_date = getattr(instance, "_original_date", None)
    old_time = getattr(instance, "_original_time", None)
    old_status = getattr(instance, "_original_status", None)

    if old_status and old_status != Booking.Status.CANCELED and instance.status == Booking.Status.CANCELED:
        notify_booking_canceled(instance)
        return

    if old_date and old_time:
        if old_date != instance.date or old_time != instance.time:
            notify_booking_updated(instance, old_date, old_time)


@receiver(pre_delete, sender=Booking)
def booking_pre_delete(sender, instance, **kwargs):
    if instance.status != Booking.Status.CANCELED:
        notify_booking_canceled(instance)
