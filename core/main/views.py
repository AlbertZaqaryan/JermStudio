import json
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.views.decorators.http import require_GET, require_POST

from .models import Booking, PlacePhoto, Room, SiteContent

VALID_LANGS = frozenset(code for code, _ in settings.LANGUAGES)


def resolve_request_language(request):
    session_lang = request.session.get("django_language")
    if session_lang in VALID_LANGS:
        return session_lang
    cookie_lang = request.COOKIES.get("django_language", "")
    if cookie_lang in VALID_LANGS:
        return cookie_lang
    accept = (request.LANGUAGE_CODE or "en")[:2]
    if accept in VALID_LANGS:
        return accept
    return "en"


def ensure_site_content_languages():
    for code, _ in settings.LANGUAGES:
        SiteContent.objects.get_or_create(language=code)


@require_POST
def set_language_preference(request):
    language = request.POST.get("language", "en")
    valid_codes = {code for code, _ in settings.LANGUAGES}
    if language not in valid_codes:
        language = "en"

    request.session["django_language"] = language
    response = redirect(request.POST.get("next") or "/")
    response.set_cookie("django_language", language)
    return response


def landing_page(request):
    ensure_site_content_languages()
    room_images = [
        static("main/images/kids-room-1.png"),
        static("main/images/kids-room-2.png"),
        static("main/images/kids-room-3.png"),
        static("main/images/kids-room-4.png"),
    ]
    rooms = list(Room.objects.all())
    for index, room in enumerate(rooms):
        room.display_image_url = room.image.url if room.image else room_images[index % len(room_images)]

    language_code = resolve_request_language(request)

    site_content, _ = SiteContent.objects.get_or_create(language=language_code)
    hero_image = (
        site_content.hero_background.url
        if site_content.hero_background
        else static("main/images/kids-room-1.png")
    )
    studio_logo_url = (
        site_content.studio_logo_image.url
        if site_content.studio_logo_image
        else static("main/images/studio-logo-reference.png")
    )
    place_photos = list(PlacePhoto.objects.all())
    if not place_photos:
        place_photos = [
            {"image_url": img, "title": f"Place Photo {index + 1}"}
            for index, img in enumerate(room_images)
        ]
    else:
        for photo in place_photos:
            photo.image_url = photo.image.url

    return render(
        request,
        "main/index.html",
        {
            "rooms": rooms,
            "hero_image": hero_image,
            "studio_logo_url": studio_logo_url,
            "place_photos": place_photos,
            "site_content": site_content,
            "available_languages": settings.LANGUAGES,
            "current_language": language_code,
        },
    )


@require_GET
def available_dates_api(request):
    days = int(request.GET.get("days", 60))
    dates = Booking.available_dates(days=days)
    return JsonResponse(
        {
            "available_dates": [d.isoformat() for d in dates],
        }
    )


@require_GET
def available_slots_api(request):
    date_value = request.GET.get("date")
    if not date_value:
        return JsonResponse({"error": "date query parameter is required."}, status=400)

    try:
        selected_date = datetime.strptime(date_value, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "date must be in YYYY-MM-DD format."}, status=400)

    slots = Booking.available_slots_for_date(selected_date)
    return JsonResponse({"date": selected_date.isoformat(), "available_slots": slots})


@require_POST
def create_booking_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    required_fields = ("first_name", "last_name", "email", "phone", "date", "time")
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return JsonResponse(
            {"error": f"Missing required fields: {', '.join(missing)}."},
            status=400,
        )

    try:
        booking_date = datetime.strptime(payload["date"], "%Y-%m-%d").date()
        booking_time = datetime.strptime(payload["time"], "%H:%M").time()
    except ValueError:
        return JsonResponse(
            {"error": "Invalid date/time format. Use YYYY-MM-DD and HH:MM."},
            status=400,
        )

    booking = Booking(
        first_name=payload["first_name"].strip(),
        last_name=payload["last_name"].strip(),
        email=payload["email"].strip(),
        phone=payload["phone"].strip(),
        date=booking_date,
        time=booking_time,
    )

    try:
        booking.full_clean()
        booking.save()
    except ValidationError as error:
        return JsonResponse({"error": error.message_dict}, status=400)
    except IntegrityError:
        return JsonResponse(
            {"error": "This slot is no longer available. Please choose another time."},
            status=409,
        )

    return JsonResponse(
        {
            "message": "Booking confirmed! We look forward to your session.",
            "booking": {
                "name": f"{booking.first_name} {booking.last_name}",
                "date": booking.date.isoformat(),
                "time": booking.time.strftime("%H:%M"),
            },
        },
        status=201,
    )
