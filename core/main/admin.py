from django.contrib import admin

from .models import Booking, PlacePhoto, Room, SiteContent, SiteSettings


admin.site.register(SiteSettings)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "created_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "date",
        "time",
        "created_at",
    )
    list_filter = ("date", "time", "created_at")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("-date", "-time")


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Language", {"fields": ("language",)}),
        (
            "Hero Section",
            {
                "description": "Upload the studio logo image for each language. Alt/fallback text is used for accessibility and when no image is set.",
                "fields": (
                    "site_name",
                    "studio_logo_image",
                    "hero_badge",
                    "hero_title",
                    "hero_subtitle",
                    "hero_button_text",
                    "hero_background",
                ),
            },
        ),
        (
            "Rooms Section",
            {
                "fields": (
                    "rooms_title",
                    "rooms_subtitle",
                    "rooms_empty_title",
                    "rooms_empty_text",
                    "room_price_prefix",
                    "room_custom_pricing_text",
                    "room_book_button_text",
                )
            },
        ),
        ("Place Section", {"fields": ("place_title", "place_subtitle")}),
        (
            "Booking Modal Texts",
            {
                "fields": (
                    "booking_modal_title",
                    "selected_room_prefix",
                    "booking_step_1",
                    "booking_step_2",
                    "booking_step_3",
                    "booking_choose_date_title",
                    "booking_choose_date_text",
                    "booking_choose_time_title",
                    "booking_choose_time_text",
                    "booking_details_title",
                    "booking_submit_text",
                    "first_name_placeholder",
                    "last_name_placeholder",
                    "email_placeholder",
                    "phone_placeholder",
                    "loading_dates_text",
                    "loading_slots_text",
                    "no_slots_text",
                    "select_date_time_text",
                    "booking_error_text",
                    "booking_success_text",
                )
            },
        ),
    )
    list_display = ("site_name", "language", "updated_at")
    list_filter = ("language",)
    search_fields = ("site_name", "hero_title", "rooms_title", "place_title")

    def has_add_permission(self, request):
        return False


@admin.register(PlacePhoto)
class PlacePhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)
