from datetime import date as date_cls
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models


class SiteSettings(models.Model):
    font_family = models.CharField(
        max_length=100,
        default='Playfair Display'
    )

    def __str__(self):
        return "Site Settings"

class Room(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(upload_to="rooms/")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return self.name


class SiteContent(models.Model):
    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("hy", "Armenian"),
        ("ru", "Russian"),
    )

    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en", unique=True)
    site_name = models.CharField(max_length=120, default="JERM STUDIO")
    studio_logo_image = models.ImageField(
        upload_to="site/logo/",
        null=True,
        blank=True,
        verbose_name="Studio logo (image)",
        help_text="PNG/SVG-style logo shown above the main title. Upload per language if designs differ.",
    )
    hero_badge = models.CharField(
        max_length=160,
        default="KIDS PHOTOGRAPHY STUDIO",
        verbose_name="Logo alt text & text fallback",
        help_text="Used as the image alt attribute for accessibility. If no logo image is uploaded, this text is shown in the styled pill instead.",
    )
    hero_title = models.CharField(max_length=180, default="JERM STUDIO")
    hero_subtitle = models.CharField(
        max_length=300,
        default="Magical and cozy sets crafted for newborn, toddler, and children portraits.",
    )
    hero_button_text = models.CharField(max_length=80, default="Explore Rooms")
    hero_background = models.ImageField(upload_to="site/hero/", null=True, blank=True)

    rooms_title = models.CharField(max_length=120, default="Kids Studio Rooms")
    rooms_subtitle = models.CharField(
        max_length=300,
        default="Soft textures, playful props, and gentle tones designed for children-focused storytelling.",
    )
    rooms_empty_title = models.CharField(max_length=120, default="Rooms Coming Soon")
    rooms_empty_text = models.CharField(
        max_length=220, default="Add rooms in the admin panel to display them here."
    )
    room_price_prefix = models.CharField(max_length=40, default="From")
    room_custom_pricing_text = models.CharField(max_length=80, default="Custom pricing")
    room_book_button_text = models.CharField(max_length=80, default="Book Now")

    place_title = models.CharField(max_length=120, default="Place")
    place_subtitle = models.CharField(
        max_length=240, default="Photos from our real studio sessions."
    )

    booking_modal_title = models.CharField(max_length=120, default="Book a Session")
    selected_room_prefix = models.CharField(max_length=80, default="Selected room")
    booking_step_1 = models.CharField(max_length=80, default="1. Date")
    booking_step_2 = models.CharField(max_length=80, default="2. Time")
    booking_step_3 = models.CharField(max_length=80, default="3. Details")
    booking_choose_date_title = models.CharField(max_length=80, default="Choose a Date")
    booking_choose_date_text = models.CharField(
        max_length=180, default="Only available dates are selectable."
    )
    booking_choose_time_title = models.CharField(max_length=80, default="Choose a Time")
    booking_choose_time_text = models.CharField(
        max_length=200, default="Time slots are shared globally across all rooms."
    )
    booking_details_title = models.CharField(max_length=80, default="Your Details")
    booking_submit_text = models.CharField(max_length=80, default="Confirm Booking")
    first_name_placeholder = models.CharField(max_length=60, default="First Name")
    last_name_placeholder = models.CharField(max_length=60, default="Last Name")
    email_placeholder = models.CharField(max_length=60, default="Email")
    phone_placeholder = models.CharField(max_length=60, default="Phone Number")
    loading_dates_text = models.CharField(max_length=120, default="Loading available dates...")
    loading_slots_text = models.CharField(max_length=120, default="Loading available slots...")
    no_slots_text = models.CharField(
        max_length=180, default="No slots available for this date. Please choose another day."
    )
    select_date_time_text = models.CharField(
        max_length=140, default="Please choose a date and time first."
    )
    booking_error_text = models.CharField(
        max_length=160, default="Unable to create booking. Please try again."
    )
    booking_success_text = models.CharField(max_length=120, default="Booking confirmed.")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Content"
        verbose_name_plural = "Site Content"
        ordering = ("language",)

    def __str__(self):
        return f"Website Content ({self.get_language_display()})"


class PlacePhoto(models.Model):
    title = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to="place/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title or f"Place Photo {self.pk}"


class Booking(models.Model):
    # Opening hours 09:00 - 21:00 (inclusive, hourly slots)
    SLOT_CHOICES = tuple((f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(9, 22))

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("date", "time")
        constraints = [
            models.UniqueConstraint(fields=("date", "time"), name="unique_booking_slot"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.date} {self.time}"

    @classmethod
    def all_time_slots(cls):
        return [slot[0] for slot in cls.SLOT_CHOICES]

    @classmethod
    def available_dates(cls, days=60):
        today = date_cls.today()
        booked = {}
        for entry in cls.objects.filter(date__gte=today, date__lte=today + timedelta(days=days)):
            booked.setdefault(entry.date, set()).add(entry.time.strftime("%H:%M"))

        full_count = len(cls.all_time_slots())
        available = []
        for i in range(days + 1):
            current = today + timedelta(days=i)
            if len(booked.get(current, set())) < full_count:
                available.append(current)
        return available

    @classmethod
    def available_slots_for_date(cls, target_date):
        booked_slots = set(
            cls.objects.filter(date=target_date).values_list("time", flat=True)
        )
        booked_strings = {slot.strftime("%H:%M") for slot in booked_slots}
        return [slot for slot in cls.all_time_slots() if slot not in booked_strings]

    def clean(self):
        available = self.available_slots_for_date(self.date)
        if self.time.strftime("%H:%M") not in available:
            raise ValidationError({"time": "This time slot is already booked."})
