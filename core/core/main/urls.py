from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.landing_page, name="home"),
    path("set-language/", views.set_language_preference, name="set_language_preference"),
    path("api/available-dates/", views.available_dates_api, name="available_dates"),
    path("api/available-slots/", views.available_slots_api, name="available_slots"),
    path("api/bookings/", views.create_booking_api, name="create_booking"),
]