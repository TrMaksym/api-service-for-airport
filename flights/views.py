from django.core.serializers import get_serializer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
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
        if hasattr(serializer.Meta.model, "user"):
            serializer.save(user=self.request.user)
        else:
            serializer.save()


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
    permission_classes = [IsAdminOrIfAuthenticated]


class AirplaneViewSet(BaseModelViewSet):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        elif self.action == "upload_image":
            return image_path
        return AirplaneSerializer

    @action(
        methods=["post"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(
            instance=airplane, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source_city",
                type={"type": "array", "items": {"type": "number"}},
                description="Source city name",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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
    permission_classes = [IsAdminOrIfAuthenticated]

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

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(UserOrAdminQuerySetMixin, BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.all()
    user_filter = {"order__user": "self.request.user"}

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketRetrieveSerializer
        return TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(order__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        order_id = self.request.data.get("order") or self.request.data.get("order_id")
        if order_id:
            order = get_object_or_404(Order, pk=order_id)
            context["order"] = order
        return context


class TicketClassViewSet(BaseModelViewSet):
    queryset = TicketClass.objects.all()
    serializer_class = TicketClassSerializer


class PromotionViewSet(BaseModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer


class PassengerViewSet(UserRestrictedMixin, BaseModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer


class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer

    @action(detail=False, methods=["get"])
    def available(self, request, flight):
        flight_id = request.query_params.get("flight")
        is_window = request.query_params.get("is_window")
        is_aisle = request.query_params.get("is_aisle")
        is_available = request.query_params.get("is_available")

        seats = Seat.objects.all()

        if flight_id:
            seats = seats.filter(flight_id=flight_id)
        if is_window is not None:
            seats = seats.filter(is_window=is_window.lower() == "true")
        if is_aisle is not None:
            seats = seats.filter(is_aisle=is_aisle.lower() == "true")
        if is_available is not None:
            seats = seats.filter(is_available=is_available.lower() == "true")

        occupied_seats_ids = Ticket.objects.filter(
            status__in=["reserved", "paid"]
        ).values_list("seat_id", flat=True)

        seats = seats.exclude(id__in=occupied_seats_ids)

        serializer = self.get_serializer(seats, many=True)
        return Response(serializer.data)


class PaymentViewSet(UserOrAdminQuerySetMixin, BaseModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    user_filter = {"order__user": "self.request.user"}

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


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

    def get_queryset(self):
        return OrderHistory.objects.filter(order__user=self.request.user)


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
