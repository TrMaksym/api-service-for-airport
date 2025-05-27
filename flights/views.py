from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from flights.models import *
from flights.serializers import *
from flights.permissions import IsAdminOrIfAuthenticated


class UserOrAdminQuerySetMixin:
    user_filter = {}

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        filters = {
            k: (self.request.user if v == "self.request.user" else v)
            for k, v in getattr(self, "user_filter", {}).items()
        }
        return self.queryset.filter(**filters)


class UserRestrictedMixin:
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrIfAuthenticated]


class CountryViewSet(BaseModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(BaseModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AirportViewSet(BaseModelViewSet):
    queryset = Airport.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportRetrieveSerializer
        return AirportSerializer


class AirportFilterView(APIView):
    permission_classes = [IsAdminOrIfAuthenticated]

    def get(self, request):
        serializer = AirportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        queryset = Airport.objects.all()

        city = data.get("city")
        if city:
            queryset = queryset.filter(city__name__icontains=city)
        name = data.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        iata = data.get("iata_code")
        if iata:
            queryset = queryset.filter(iata_code__icontains=iata)

        return Response(AirportListSerializer(queryset, many=True).data)


class RouteViewSet(BaseModelViewSet):
    queryset = Route.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer


class RouteFilterView(APIView):
    permission_classes = [IsAdminOrIfAuthenticated]

    def get(self, request):
        serializer = RouteFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        queryset = Route.objects.all()

        if source := data.get("source_city"):
            queryset = queryset.filter(source__city__name__icontains=source)
        if destination := data.get("destination_city"):
            queryset = queryset.filter(destination__city__name__icontains=destination)
        if min_dist := data.get("min_distance"):
            queryset = queryset.filter(distance__gte=min_dist)
        if max_dist := data.get("max_distance"):
            queryset = queryset.filter(distance__lte=max_dist)

        return Response(RouteListSerializer(queryset, many=True).data)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(BaseModelViewSet):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer


class CrewViewSet(BaseModelViewSet):
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        if self.action == "retrieve":
            return CrewRetrieveSerializer
        return CrewSerializer


class FlightViewSet(BaseModelViewSet):
    queryset = Flight.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer


class FlightFilterView(APIView):
    permission_classes = [IsAdminOrIfAuthenticated]

    def get(self, request):
        serializer = FlightFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        queryset = Flight.objects.all()

        if dt_after := data.get("departure_time_after"):
            queryset = queryset.filter(departure_time__gte=dt_after)
        if dt_before := data.get("departure_time_before"):
            queryset = queryset.filter(departure_time__lte=dt_before)
        if source := data.get("source_city"):
            queryset = queryset.filter(route__source__city__name__icontains=source)
        if destination := data.get("destination_city"):
            queryset = queryset.filter(
                route__destination__city__name__icontains=destination
            )
        if status := data.get("status"):
            queryset = queryset.filter(status=status)

        return Response(FlightListSerializer(queryset, many=True).data)


class OrderViewSet(UserRestrictedMixin, BaseModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer


class TicketViewSet(UserOrAdminQuerySetMixin, BaseModelViewSet):
    queryset = Ticket.objects.all()
    user_filter = {"order__user": "self.request.user"}

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketRetrieveSerializer
        return TicketSerializer


class TicketClassViewSet(BaseModelViewSet):
    queryset = TicketClass.objects.all()
    serializer_class = TicketClassSerializer


class PromotionViewSet(BaseModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer


class PassengerViewSet(UserRestrictedMixin, BaseModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer


class SeatViewSet(BaseModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


class PaymentViewSet(UserOrAdminQuerySetMixin, BaseModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    user_filter = {"order__user": "self.request.user"}


class ExtraServiceViewSet(UserOrAdminQuerySetMixin, BaseModelViewSet):
    queryset = ExtraService.objects.all()
    serializer_class = ExtraServiceSerializer
    user_filter = {"order__user": "self.request.user"}


class FlightHistoryViewSet(BaseModelViewSet):
    queryset = FlightHistory.objects.all()
    serializer_class = FlightHistorySerializer


class OrderHistoryViewSet(UserOrAdminQuerySetMixin, BaseModelViewSet):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer
    user_filter = {"order__user": "self.request.user"}


class ReviewViewSet(UserOrAdminQuerySetMixin, BaseModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    user_filter = {"user": "self.request.user"}


class AirlineViewSet(BaseModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer


class RefundPolicyViewSet(BaseModelViewSet):
    queryset = RefundPolicy.objects.all()
    serializer_class = RefundPolicySerializer


class NotificationViewSet(UserOrAdminQuerySetMixin, BaseModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    user_filter = {"user": "self.request.user"}
