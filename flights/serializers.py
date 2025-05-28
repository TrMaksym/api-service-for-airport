from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from flights.models import (
    TicketClass,
    Ticket,
    Order,
    Crew,
    Flight,
    Airplane,
    AirplaneType,
    Route,
    Airport,
    City,
    Country,
    Promotion,
    Passenger,
    Seat,
    Payment,
    ExtraService,
    FlightHistory,
    OrderHistory,
    Review,
    Airline,
    RefundPolicy,
    Notification,
)
from user.serializers import UserSerializer


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "country")
        extra_kwargs = {"country": {"help_text": "Name of the country"}}


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = City
        fields = ("id", "name", "country")
        extra_kwargs = {
            "name": {"help_text": "Name of the city"},
            "country": {"help_text": "Country where the city is located"},
        }


class AirportSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source="city", write_only=True
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "city", "city_id")
        extra_kwargs = {
            "name": {"help_text": "Airport name"},
        }


class AirportListSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Airport
        fields = ("id", "name", "city")
        extra_kwargs = {
            "name": {"help_text": "Airport name"},
        }


class AirportRetrieveSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "city")
        extra_kwargs = {
            "name": {"help_text": "Airport name"},
        }


class AirportFilterSerializer(serializers.Serializer):
    city = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    iata_code = serializers.CharField(required=False)

    class Meta:
        fields = ("city", "name", "iata_code")

    def validate(self, data):
        if not any(data.get(field) for field in ["city", "name"]):
            raise serializers.ValidationError(
                "At least one filter (city, name) must be provided."
            )
        return data


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), source="source", write_only=True
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), source="destination", write_only=True
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "source_id",
            "destination_id",
            "distance",
        )
        extra_kwargs = {
            "distance": {
                "help_text": "Distance between source and destination in kilometers"
            }
        }

    def validate(self, data):
        if data.get("source") == data.get("destination"):
            raise serializers.ValidationError(
                "Source and destination airports must be different."
            )
        return data


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")
        extra_kwargs = {
            "distance": {
                "help_text": "Distance between source and destination in kilometers"
            }
        }


class RouteRetrieveSerializer(serializers.ModelSerializer):
    source = AirportRetrieveSerializer(read_only=True)
    destination = AirportRetrieveSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")
        extra_kwargs = {
            "distance": {
                "help_text": "Distance between source and destination in kilometers"
            }
        }


class RouteFilterSerializer(serializers.Serializer):
    source_city = serializers.CharField(required=False)
    destination_city = serializers.CharField(required=False)
    min_distance = serializers.IntegerField(required=False)
    max_distance = serializers.IntegerField(required=False)

    class Meta:
        fields = ("source_city", "destination_city", "min_distance", "max_distance")

    def validate(self, data):
        if (
            data.get("min_distance")
            and data.get("max_distance")
            and data["min_distance"] > data["max_distance"]
        ):
            raise serializers.ValidationError(
                "min_distance must be less than or equal to max_distance."
            )
        if data.get("source_city") == data.get("destination_city"):
            raise serializers.ValidationError(
                "Source and destination cities must be different."
            )
        return data


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")
        extra_kwargs = {"name": {"help_text": "Type of the airplane"}}


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all(), source="airplane_type", write_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "airplane_type_id",
        )
        extra_kwargs = {
            "name": {"help_text": "Airplane model name"},
            "rows": {"help_text": "Number of rows in airplane"},
            "seats_in_row": {"help_text": "Number of seats in each row"},
        }


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")
        extra_kwargs = {
            "name": {"help_text": "Airplane model name"},
            "rows": {"help_text": "Number of rows in airplane"},
            "seats_in_row": {"help_text": "Number of seats in each row"},
        }


class AirplaneRetrieveSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")
        extra_kwargs = {
            "name": {"help_text": "Airplane model name"},
            "rows": {"help_text": "Number of rows in airplane"},
            "seats_in_row": {"help_text": "Number of seats in each row"},
        }


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")
        extra_kwargs = {
            "first_name": {"help_text": "Crew member first name"},
            "last_name": {"help_text": "Crew member last name"},
        }


class CrewListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ("id", "full_name")
        extra_kwargs = {"full_name": {"help_text": "Full name of the crew member"}}

    @staticmethod
    def get_full_name(obj):
        return f"{obj.first_name} {obj.last_name}"


class CrewRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")
        extra_kwargs = {
            "first_name": {"help_text": "Crew member first name"},
            "last_name": {"help_text": "Crew member last name"},
        }


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(), source="route", write_only=True
    )
    airplane = AirplaneSerializer(read_only=True)
    airplane_id = serializers.PrimaryKeyRelatedField(
        queryset=Airplane.objects.all(), source="airplane", write_only=True
    )
    crew = CrewSerializer(many=True, read_only=True)
    crew_ids = serializers.PrimaryKeyRelatedField(
        queryset=Crew.objects.all(), many=True, source="crew", write_only=True
    )

    country = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "route_id",
            "airplane",
            "airplane_id",
            "departure_time",
            "arrival_time",
            "crew",
            "crew_ids",
            "country",
            "status",
        )

        extra_kwargs = {
            "route": {"help_text": "Route of the flight"},
            "airplane": {"help_text": "Airplane used for the flight"},
            "departure_time": {"help_text": "Departure time of the flight"},
            "arrival_time": {"help_text": "Arrival time of the flight"},
            "status": {"help_text": "Current status of the flight"},
        }

    def get_country(self, obj):
        return obj.route.source.city.country.country

    def validate(self, data):
        departure = data.get("departure_time")
        arrival = data.get("arrival_time")
        if departure and arrival and departure >= arrival:
            raise serializers.ValidationError(
                "Departure time must be before arrival time."
            )
        return data

    def create(self, validated_data):
        crew_data = validated_data.pop("crew", [])
        with transaction.atomic():
            flight = Flight.objects.create(**validated_data)
            flight.crew.set(crew_data)
        return flight

    def update(self, instance, validated_data):
        crew_data = validated_data.pop("crew", None)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if crew_data is not None:
                instance.crew.set(crew_data)
        return instance


class FlightListSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = serializers.SlugRelatedField(read_only=True, slug_field="name")
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="last_name"
    )
    departure_time = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    arrival_time = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    status = serializers.CharField(source="get_status_display", read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "duration",
            "status",
            "crew",
        )

    @staticmethod
    def get_duration(obj):
        duration = obj.arrival_time - obj.departure_time
        return round(duration.total_seconds() / 3600, 2)


class FlightRetrieveSerializer(serializers.ModelSerializer):
    route = RouteRetrieveSerializer(read_only=True)
    airplane = AirplaneRetrieveSerializer(read_only=True)
    crew = CrewRetrieveSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "duration",
            "crew",
            "status",
            "available_seats",
        )

    @staticmethod
    def get_duration(obj):
        duration = obj.arrival_time - obj.departure_time
        return round(duration.total_seconds() / 3600, 2)

    @staticmethod
    def get_available_seats(obj):
        total_seats = obj.airplane.rows * obj.airplane.seats_in_row
        taken = Ticket.objects.filter(seat__flight=obj).count()
        return total_seats - taken


class FlightFilterSerializer(serializers.Serializer):
    departure_time_after = serializers.DateTimeField(required=False)
    departure_time_before = serializers.DateTimeField(required=False)
    source_city = serializers.CharField(required=False)
    destination_city = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=Flight.STATUS_CHOICES, required=False)

    class Meta:
        fields = (
            "departure_time_after",
            "departure_time_before",
            "source_city",
            "destination_city",
            "status",
        )

    def validate(self, data):
        if data.get("departure_time_after") and data.get("departure_time_before"):
            if data["departure_time_after"] > data["departure_time_before"]:
                raise serializers.ValidationError(
                    "departure_time_after must be earlier than departure_time_before."
                )
        if data.get("source_city") == data.get("destination_city"):
            raise serializers.ValidationError(
                "Source and destination cities must be different."
            )
        return data


class TicketSerializer(serializers.ModelSerializer):
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())
    ticket_class = serializers.PrimaryKeyRelatedField(
        queryset=TicketClass.objects.all()
    )
    seat_number = serializers.ReadOnlyField(source="seat.seat_number")
    row = serializers.ReadOnlyField(source="seat.row")
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES, default="reserved")

    class Meta:
        model = Ticket
        fields = (
            "id",
            "order",
            "seat",
            "ticket_class",
            "seat_number",
            "row",
            "base_price",
            "status",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=("seat", "order", "ticket_class"),
            )
        ]

    def validate_seat(self, value):
        if Ticket.objects.filter(seat=value, status__in=['reserved', 'paid']).exists():
            raise ValidationError(f"Seat {value} is already taken.")
        return value


class TicketListSerializer(serializers.ModelSerializer):
    order = serializers.SlugRelatedField(read_only=True, slug_field="id")
    ticket_class = serializers.SlugRelatedField(read_only=True, slug_field="name")
    seat_number = serializers.ReadOnlyField(source="seat.seat_number")
    row = serializers.ReadOnlyField(source="seat.row")
    status = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "order",
            "seat_number",
            "row",
            "ticket_class",
            "base_price",
            "status",
        )


class TicketRetrieveSerializer(TicketSerializer):
    order = serializers.SlugRelatedField(read_only=True, slug_field="id")
    ticket_class = serializers.SlugRelatedField(read_only=True, slug_field="name")
    flight = serializers.CharField(source="seat.flight.route.__str__", read_only=True)
    seat = serializers.CharField(source="seat.get_seat_display", read_only=True)
    seat_number = serializers.ReadOnlyField(source="seat.seat_number")
    row = serializers.ReadOnlyField(source="seat.row")
    status = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "order",
            "seat",
            "ticket_class",
            "seat_number",
            "row",
            "base_price",
            "status",
            "flight",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets_info = TicketRetrieveSerializer(many=True, read_only=True, source='tickets')
    tickets = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ticket.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Order
        fields = ('id', 'created_at', 'user', 'ticket_class', 'extra_services', 'tickets', 'tickets_info')
        read_only_fields = ('user', 'created_at')

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets", None)
            order = Order.objects.create(**validated_data)
            Ticket.objects.bulk_create([
                Ticket(order=order, **ticket)
                for ticket in tickets_data
            ])
            return order

    def update(self, instance, validated_data):
        tickets = validated_data.pop('tickets', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tickets is not None:
            instance.tickets.all().update(order=None)
            for ticket in tickets:
                ticket.order = instance
                ticket.save()

        return instance


class TicketClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketClass
        fields = ("id", "name", "price_multiplier")
        extra_kwargs = {
            "name": {"help_text": "Name of the ticket class (e.g., Economy, Business)"},
            "price_multiplier": {"help_text": "Price multiplier for the ticket class"},
        }


class ExtraServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraService
        fields = ("id", "name", "price")
        extra_kwargs = {
            "name": {"help_text": "Name of the extra service"},
            "price": {"help_text": "Price of the extra service"},
        }


class OrderListSerializer(OrderSerializer):
    tickets_info = TicketRetrieveSerializer(many=True, read_only=True, source="tickets")
    created_at = serializers.DateTimeField(format="%d %b %Y, %H:%M", read_only=True)
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    ticket_class = TicketClassSerializer(read_only=True)
    extra_services = ExtraServiceSerializer(read_only=True, many=True)


class PromotionSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = (
            "id",
            "name",
            "discount_percent",
            "start_date",
            "end_date",
            "is_active",
        )
        extra_kwargs = {
            "name": {"help_text": "Name of the promotion"},
            "discount_percent": {"help_text": "Discount percentage"},
            "start_date": {"help_text": "Start date of the promotion"},
            "end_date": {"help_text": "End date of the promotion"},
        }

    @staticmethod
    def get_is_active(obj):
        return obj.is_active()


class PassengerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Passenger
        fields = ("id", "user", "phone", "passport_number")
        extra_kwargs = {
            "phone": {"help_text": "Passenger's phone number"},
            "passport_number": {"help_text": "Passenger's passport number"},
        }


class SeatSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)

    class Meta:
        model = Seat
        fields = (
            "id",
            "flight",
            "row",
            "seat_number",
            "is_window",
            "is_aisle",
            "is_available",
        )
        extra_kwargs = {
            "row": {"help_text": "Row number of the seat"},
            "seat_number": {"help_text": "Seat number in the row"},
            "is_window": {"help_text": "Indicates if the seat is by the window"},
            "is_aisle": {"help_text": "Indicates if the seat is by the aisle"},
            "is_available": {"help_text": "Indicates if the seat is available"},
        }

    def validate(self, data):
        flight = data.get("flight")
        if flight is None:
            raise serializers.ValidationError("Flight must be specified.")

        airplane = flight.airplane

        row = data.get("row")
        seat_number = data.get("seat_number")
        is_window = data.get("is_window", False)
        is_aisle = data.get("is_aisle", False)

        if row > airplane.rows:
            raise serializers.ValidationError(
                f"Row number {row} exceeds total rows in airplane ({airplane.rows})"
            )
        if seat_number > airplane.seats_in_row:
            raise serializers.ValidationError(
                f"Seat number {seat_number} exceeds seats per row ({airplane.seats_in_row})"
            )
        if is_window and seat_number not in (1, airplane.seats_in_row):
            raise serializers.ValidationError(
                "Only first or last seats in a row can be window seats."
            )
        if is_aisle and seat_number in (1, airplane.seats_in_row):
            raise serializers.ValidationError(
                "Window seats cannot be aisle seats."
            )

        return data


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES, default="pending")
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "order", "amount", "payment_date", "status")
        extra_kwargs = {
            "amount": {"help_text": "Payment amount"},
            "payment_date": {"help_text": "Date of the payment"},
            "status": {"help_text": "Payment status (e.g., Pending, Successful)"},
        }


class FlightHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = FlightHistory
        fields = ("id", "flight", "changed_at", "changed_by", "change_description")
        read_only_fields = ("changed_at", "changed_by")
        extra_kwargs = {
            "change_description": {
                "help_text": "Description of the change made to the flight"
            }
        }

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["changed_by"] = request.user
        else:
            raise serializers.ValidationError(
                "Users must be authenticated for creating flight history."
            )
        return super().create(validated_data)


class OrderHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = OrderHistory
        fields = ("id", "order", "changed_at", "changed_by", "change_description")
        read_only_fields = ("changed_at", "changed_by")
        extra_kwargs = {
            "change_description": {
                "help_text": "Description of the change made to the order"
            }
        }

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["changed_by"] = request.user
        else:
            raise serializers.ValidationError("Users must be authenticated.")
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    flight = FlightSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "user", "flight", "rating", "comment", "created_at")
        extra_kwargs = {
            "comment": {"help_text": "Comment provided by the user"},
            "created_at": {"help_text": "Timestamp when the review was created"},
        }

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class AirlineSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Airline
        fields = ("id", "name", "country", "iata_code")
        extra_kwargs = {
            "name": {"help_text": "Name of the airline"},
            "iata_code": {"help_text": "IATA code of the airline"},
        }


class RefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundPolicy
        fields = ("id", "name", "refundable", "penalty_percent", "valid_until")
        extra_kwargs = {
            "name": {"help_text": "Name of the refund policy"},
            "refundable": {"help_text": "Indicates if the ticket is refundable"},
            "penalty_percent": {"help_text": "Percentage penalty for refund"},
            "valid_until": {"help_text": "Duration until the refund is valid"},
        }


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "user", "message", "created_at", "read")
        extra_kwargs = {
            "message": {"help_text": "Notification message"},
            "read": {"help_text": "Indicates if the notification has been read"},
        }

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")