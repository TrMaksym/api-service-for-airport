from rest_framework import routers
from django.urls import path, include
from flights.views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneViewSet,
    AirplaneTypeViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
    TicketViewSet,
    TicketClassViewSet,
    PromotionViewSet,
    PassengerViewSet,
    SeatViewSet,
    PaymentViewSet,
    ExtraServiceViewSet,
    FlightHistoryViewSet,
    OrderHistoryViewSet,
    ReviewViewSet,
    AirlineViewSet,
    RefundPolicyViewSet,
    NotificationViewSet,
    CityViewSet,
    CountryViewSet,
)

router = routers.DefaultRouter()
router.register(r"airports", AirportViewSet, basename="airport")
router.register(r"routes", RouteViewSet, basename="route")
router.register(r"airplanes", AirplaneViewSet, basename="airplane")
router.register(r"airplane-types", AirplaneTypeViewSet, basename="airplanetype")
router.register(r"crews", CrewViewSet, basename="crew")
router.register(r"flights", FlightViewSet, basename="flight")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"tickets", TicketViewSet, basename="ticket")
router.register(r"ticket-classes", TicketClassViewSet, basename="ticketclass")
router.register(r"promotions", PromotionViewSet, basename="promotion")
router.register(r"passengers", PassengerViewSet, basename="passenger")
router.register(r"seats", SeatViewSet, basename="seat")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"extra-services", ExtraServiceViewSet, basename="extraservice")
router.register(r"flight-history", FlightHistoryViewSet, basename="flighthistory")
router.register(r"order-history", OrderHistoryViewSet, basename="orderhistory")
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"airlines", AirlineViewSet, basename="airline")
router.register(r"refund-policies", RefundPolicyViewSet, basename="refundpolicy")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"cities", CityViewSet, basename="city")
router.register(r"countries", CountryViewSet, basename="country")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "flight"
