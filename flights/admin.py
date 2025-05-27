from django.contrib import admin
from .models import (
    Airport, Route, Airplane, AirplaneType, Crew,
    Flight, Order, Ticket, TicketClass, Promotion,
    Passenger, Seat, Payment, ExtraService,
    FlightHistory, OrderHistory, Review,
    Airline, RefundPolicy, Notification,
    City, Country
)

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
    search_fields = ("name", "city__name")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source__name", "destination__name")


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "airplane_type")
    search_fields = ("name",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "airplane", "departure_time", "arrival_time", "status",)
    search_fields = ("id",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__email",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "seat", "ticket_class", "status")
    search_fields = ("order__id",)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "passport_number")
    search_fields = ("user__first_name", "user__last_name", "user__email")


admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(TicketClass)
admin.site.register(Promotion)
admin.site.register(Seat)
admin.site.register(Payment)
admin.site.register(ExtraService)
admin.site.register(FlightHistory)
admin.site.register(OrderHistory)
admin.site.register(Review)
admin.site.register(Airline)
admin.site.register(RefundPolicy)
admin.site.register(Notification)
admin.site.register(City)
admin.site.register(Country)
