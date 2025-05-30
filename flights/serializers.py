from django.db import transaction
from rest_framework import serializers
from django.db.models import Q
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


def validate_source_destination(
    source, destination, source_field="source", destination_field="destination"
):
    if source == destination:
        raise serializers.ValidationError(
            f"{source_field.capitalize()} and {destination_field.capitalize()} must be different."
        )
    return True


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "country")
        extra_kwargs = {"country": {"help_text": "Name of the country"}}


class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.SlugRelatedField(
        source='country',
        read_only=True,
        slug_field="country",
    )
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all()
    )

    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'country_name']


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
        print(f"Validating AirportFilter: {data}")
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
        print(
            f"Validating Route: source={data.get('source')}, destination={data.get('destination')}"
        )
        validate_source_destination(data.get("source"), data.get("destination"))
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
        print(f"Validating RouteFilter: {data}")
        if data.get("min_distance") and data.get("max_distance"):
            if data["min_distance"] > data["max_distance"]:
                raise serializers.ValidationError(
                    "min_distance must be less than or equal to max_distance."
                )
        validate_source_destination(
            data.get("source_city"),
            data.get("destination_city"),
            source_field="source_city",
            destination_field="destination_city",
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
            "base_price"
        )
        read_only_fields = ["id", "country"]
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
        print(f"Validating Flight: {data}")
        departure = data.get("departure_time")
        arrival = data.get("arrival_time")
        if departure and arrival and departure >= arrival:
            raise serializers.ValidationError(
                "Departure time must be before arrival time."
            )
        return data

    def create(self, validated_data):
        crew_data = validated_data.pop("crew", [])
        print(f"Creating Flight with data: {validated_data}")
        with transaction.atomic():
            flight = Flight.objects.create(**validated_data)
            flight.crew.set(crew_data)
        return flight

    def update(self, instance, validated_data):
        crew_data = validated_data.pop("crew", None)
        print(f"Updating Flight {instance.id} with data: {validated_data}")
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
    available_seats_count = serializers.SerializerMethodField()

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
            "available_seats_count",
        )
        read_only_fields = ["id", "duration", "available_seats_count"]

    @staticmethod
    def get_duration(obj):
        duration = obj.arrival_time - obj.departure_time
        return round(duration.total_seconds() / 3600, 2)

    @staticmethod
    def get_available_seats_count(obj):
        count = Seat.objects.filter(flight=obj, is_available=True).count()
        print(f"Flight {obj.id} has {count} available seats")
        return count


class FlightRetrieveSerializer(serializers.ModelSerializer):
    route = RouteRetrieveSerializer(read_only=True)
    airplane = AirplaneRetrieveSerializer(read_only=True)
    crew = CrewRetrieveSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()
    available_seats_count = serializers.SerializerMethodField()

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
            "available_seats_count",
        )
        read_only_fields = ["id", "duration", "available_seats_count"]

    @staticmethod
    def get_duration(obj):
        duration = obj.arrival_time - obj.departure_time
        return round(duration.total_seconds() / 3600, 2)

    @staticmethod
    def get_available_seats_count(obj):
        count = Seat.objects.filter(flight=obj, is_available=True).count()
        print(f"Flight {obj.id} has {count} available seats")
        return count


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
        print(f"Validating FlightFilter: {data}")
        if data.get("departure_time_after") and data.get("departure_time_before"):
            if data["departure_time_after"] > data["departure_time_before"]:
                raise serializers.ValidationError(
                    "departure_time_after must be earlier than departure_time_before."
                )
        validate_source_destination(
            data.get("source_city"),
            data.get("destination_city"),
            source_field="source_city",
            destination_field="destination_city",
        )
        return data


class TicketSerializer(serializers.ModelSerializer):
    order_display = serializers.SerializerMethodField()
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())
    ticket_class = serializers.PrimaryKeyRelatedField(
        queryset=TicketClass.objects.all()
    )
    seat_number = serializers.ReadOnlyField(source="seat.seat_number")
    row = serializers.ReadOnlyField(source="seat.row")
    base_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "order",
            "order_display",
            "seat",
            "ticket_class",
            "seat_number",
            "row",
            "base_price",
            "status",
        )
        read_only_fields = ("id", "order", "base_price", "seat_number", "row", "status")

    def get_order_display(self, obj):
        return str(obj.order)

    def validate_seat(self, value):
        print(f"Validating seat {value} for ticket")
        if Ticket.objects.filter(seat=value, status__in=["reserved", "paid"]).exists():
            raise serializers.ValidationError(f"Seat {value} is already taken.")
        return value

    def create(self, validated_data):
        order = self.context.get("order")
        if not order:
            raise serializers.ValidationError("Order must be specified.")
        print(f"Creating ticket for order {order.id}, seat {validated_data['seat']}")
        validated_data["order"] = order
        validated_data["base_price"] = (
            validated_data["seat"].flight.base_price
            * validated_data["ticket_class"].price_multiplier
        )
        validated_data["status"] = "reserved"
        return super().create(validated_data)


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
        read_only_fields = ("id", "order", "seat_number", "row", "base_price", "status")


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
        read_only_fields = (
            "id",
            "order",
            "seat",
            "seat_number",
            "row",
            "base_price",
            "status",
            "flight",
        )


class OrderSerializer(serializers.ModelSerializer):
    flight = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all(), write_only=True
    )
    ticket_class = serializers.PrimaryKeyRelatedField(
        queryset=TicketClass.objects.all()
    )
    extra_services = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ExtraService.objects.all(), required=False
    )
    seat_ids = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(),
        many=True,
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="List of seat IDs to reserve",
    )
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "ticket_class",
            "extra_services",
            "flight",
            "seat_ids",
            "tickets",
        ]
        read_only_fields = ["id", "user", "tickets"]
        extra_kwargs = {
            "ticket_class": {"help_text": "Class of the ticket (e.g., Economy)"},
            "extra_services": {"help_text": "Optional extra services for the order"},
        }

    def validate(self, data):
        flight = data.get("flight")
        seat_ids = data.get("seat_ids", [])

        print(f"Validating Order: flight={flight}, seat_ids={seat_ids}")
        if not flight:
            raise serializers.ValidationError("Flight ID is required")

        available_seats = Seat.objects.filter(flight=flight, is_available=True)
        print(f"Available seats for Flight {flight.id}: {available_seats.count()}")
        if not available_seats.exists():
            raise serializers.ValidationError("No available seats")

        if seat_ids:
            seat_ids_list = [seat.id for seat in seat_ids]
            seats = Seat.objects.filter(
                id__in=seat_ids_list, flight=flight, is_available=True
            )
            if seats.count() != len(seat_ids):
                invalid_seats = set(seat_ids_list) - set(
                    seats.values_list("id", flat=True)
                )
                raise serializers.ValidationError(
                    f"Invalid or unavailable seat IDs: {invalid_seats}"
                )

            if len(seat_ids) > available_seats.count():
                raise serializers.ValidationError(
                    f"Requested {len(seat_ids)} seats, but only {available_seats.count()} available"
                )

            existing_tickets = Ticket.objects.filter(
                seat__in=seat_ids, status__in=["reserved", "paid"]
            ).values_list("seat_id", flat=True)
            if existing_tickets:
                raise serializers.ValidationError(
                    f"Seats {list(existing_tickets)} are already taken"
                )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        flight = validated_data.pop("flight")
        seat_ids = validated_data.pop("seat_ids", [])
        extra_services = validated_data.pop("extra_services", [])
        validated_data.pop("user", None)

        print(
            f"Creating order for user {user}, flight {flight.id}, seats={[seat.id for seat in seat_ids]}"
        )
        with transaction.atomic():
            order = Order.objects.create(user=user, **validated_data)
            order.extra_services.set(extra_services)

            if seat_ids:
                seat_ids_list = [seat.id for seat in seat_ids]
                seats_to_reserve = Seat.objects.filter(
                    id__in=seat_ids_list, flight=flight, is_available=True
                ).select_for_update()
                if seats_to_reserve.count() != len(seat_ids):
                    raise serializers.ValidationError(
                        "Some seats are no longer available"
                    )
            else:
                seats_to_reserve = Seat.objects.filter(
                    flight=flight, is_available=True
                ).select_for_update()[:1]
                if not seats_to_reserve:
                    raise serializers.ValidationError(
                        "No available seats on this flight"
                    )

            for seat in seats_to_reserve:
                if (
                    not seat.is_available
                    or Ticket.objects.filter(
                        seat=seat, status__in=["reserved", "paid"]
                    ).exists()
                ):
                    raise serializers.ValidationError(
                        f"Seat {seat.id} is no longer available"
                    )
                seat.is_available = False
                seat.save()
                print(f"Reserving seat {seat.id} for order {order.id}")
                Ticket.objects.create(
                    order=order,
                    seat=seat,
                    ticket_class=order.ticket_class,
                    base_price=seat.flight.base_price,
                    status="reserved",
                )

            return order

    def update(self, instance, validated_data):
        print(f"Updating Order {instance.id}: {validated_data}")
        extra_services_data = validated_data.pop("extra_services", [])
        seat_ids = validated_data.pop("seat_ids", None)
        validated_data.pop("user", None)

        instance.ticket_class = validated_data.get(
            "ticket_class", instance.ticket_class
        )
        instance.extra_services.set(extra_services_data)
        instance.save()

        if seat_ids is not None:
            current_tickets = instance.tickets.all()
            current_seat_ids = {ticket.seat.id for ticket in current_tickets}
            new_seat_ids = {seat.id for seat in seat_ids}

            for ticket in current_tickets:
                if ticket.seat.id not in new_seat_ids:
                    ticket.seat.is_available = True
                    ticket.seat.save()
                    ticket.delete()

            for seat in seat_ids:
                if seat.id not in current_seat_ids:
                    if (
                        not seat.is_available
                        or Ticket.objects.filter(
                            seat=seat, status__in=["reserved", "paid"]
                        ).exists()
                    ):
                        raise serializers.ValidationError(
                            f"Seat {seat.id} is not available"
                        )
                    seat.is_available = False
                    seat.save()
                    Ticket.objects.create(
                        order=instance,
                        seat=seat,
                        ticket_class=instance.ticket_class,
                        base_price=seat.flight.base_price,
                        status="reserved",
                    )

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
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%d %b %Y, %H:%M", read_only=True)
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    ticket_class = TicketClassSerializer(read_only=True)
    extra_services = ExtraServiceSerializer(read_only=True, many=True)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + [
            "tickets",
            "user",
            "created_at",
            "ticket_class",
            "extra_services",
        ]
        read_only_fields = ["id", "user", "tickets", "created_at"]


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
        read_only_fields = ("id", "user")
        extra_kwargs = {
            "phone": {"help_text": "Passenger's phone number"},
            "passport_number": {"help_text": "Passenger's passport number"},
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request", None)
        if request and request.user == instance.user:
            return rep
        rep.pop("phone", None)
        rep.pop("passport_number", None)
        return rep


class SeatSerializer(serializers.ModelSerializer):
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    display_name = serializers.SerializerMethodField()

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
            "display_name",
        )
        read_only_fields = ("id", "display_name")
        extra_kwargs = {
            "row": {"help_text": "Row number of the seat"},
            "seat_number": {"help_text": "Seat number in the row"},
            "is_window": {"help_text": "Indicates if the seat is by the window"},
            "is_aisle": {"help_text": "Indicates if the seat is by the aisle"},
            "is_available": {"help_text": "Indicates if the seat is available"},
        }

    def get_display_name(self, obj):
        return f"Row {obj.row} Seat {obj.seat_number}"

    def validate(self, data):
        print(f"Validating Seat: {data}")
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
            raise serializers.ValidationError("Window seats cannot be aisle seats.")

        return data


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES, default="pending")
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Payment
        fields = ("id", "order", "payment_date", "status", "amount")
        read_only_fields = ("id", "order")
        extra_kwargs = {
            "payment_date": {"help_text": "Date of the payment"},
            "status": {"help_text": "Payment status (e.g., Pending, Successful)"},
        }

    def create(self, validated_data):
        order = validated_data.pop("order")
        validated_data["amount"] = order.total_price()
        payment = Payment.objects.create(order=order, **validated_data)
        return payment


class FlightHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = FlightHistory
        fields = ("id", "flight", "changed_at", "changed_by", "change_description")
        read_only_fields = ("id", "changed_at", "changed_by")
        extra_kwargs = {
            "change_description": {
                "help_text": "Description of the change made to the flight"
            }
        }

    def create(self, validated_data):
        request = self.context.get("request")
        print(f"Creating FlightHistory: {validated_data}")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["changed_by"] = request.user
        else:
            raise serializers.ValidationError(
                "Users must be authenticated for creating flight history."
            )
        return super().create(validated_data)


class OrderHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrderHistory
        fields = ("id", "order", "changed_at", "changed_by", "change_description")
        read_only_fields = ("id", "order", "changed_at", "changed_by")
        extra_kwargs = {
            "change_description": {
                "help_text": "Description of the change made to the order"
            }
        }

    def create(self, validated_data):
        request = self.context.get("request")
        print(f"Creating OrderHistory: {validated_data}")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["changed_by"] = request.user
        else:
            raise serializers.ValidationError("Users must be authenticated.")
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.user != instance.order.user:
            rep["order"] = f"Order {instance.order.id}"
            rep["change_description"] = (
                "You don't have permission to view this information."
            )
            rep.pop("changed_by", None)
        return rep


class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    flight = FlightSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "user", "flight", "rating", "comment", "created_at")
        read_only_fields = ("id", "user", "flight", "created_at")
        extra_kwargs = {
            "comment": {"help_text": "Comment provided by the user"},
            "created_at": {"help_text": "Timestamp when the review was created"},
        }

    def validate_rating(self, value):
        print(f"Validating Review rating: {value}")
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class AirlineSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Airline
        fields = ("id", "name", "country", "iata_code")
        read_only_fields = ("id",)
        extra_kwargs = {
            "name": {"help_text": "Name of the airline"},
            "iata_code": {"help_text": "IATA code of the airline"},
        }


class RefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundPolicy
        fields = ("id", "name", "refundable", "penalty_percent", "valid_until")
        read_only_fields = ("id",)
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
        read_only_fields = ("id", "user", "created_at")
        extra_kwargs = {
            "message": {"help_text": "Notification message"},
            "read": {"help_text": "Indicates if the notification has been read"},
        }
