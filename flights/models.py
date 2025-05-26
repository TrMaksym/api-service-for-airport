from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError


class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.city})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, related_name="routes_from", on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Airport, related_name="routes_to", on_delete=models.CASCADE
    )
    distance = models.PositiveIntegerField()

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination must be different")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("delayed", "Delayed"),
        ("cancelled", "Cancelled"),
        ("in_air", "In Air"),
    ]

    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )

    def __str__(self):
        return f"Flight {self.id} from {self.route.source.name} to {self.route.destination.name}"

    @property
    def duration(self):
        return self.arrival_time - self.departure_time

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self.generate_seats()

    def generate_seats(self):
        rows = self.airplane.rows
        seats_in_row = self.airplane.seats_in_row

        for row in range(1, rows + 1):
            for seat_number in range(1, seats_in_row + 1):
                Seat.objects.create(
                    flight=self,
                    row=row,
                    seat_number=seat_number,
                    is_window=seat_number in [1, seats_in_row],
                    is_aisle=(
                        seat_number in [2, seats_in_row - 1]
                        if seats_in_row >= 4
                        else False
                    ),
                )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def total_price(self):
        tickets_price = sum(ticket.get_price() for ticket in self.tickets.all())
        services_price = sum(service.price for service in self.extraservices.all())
        return tickets_price + services_price

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class TicketClass(models.Model):
    name = models.CharField(max_length=50)  # Economy, Business тощо
    price_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("reserved", "Reserved"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    seat = models.OneToOneField("Seat", on_delete=models.PROTECT)
    order = models.ForeignKey(Order, related_name="tickets", on_delete=models.CASCADE)
    ticket_class = models.ForeignKey(TicketClass, on_delete=models.PROTECT)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="reserved")

    class Meta:
        unique_together = ("row", "seat", "flight")

    def get_price(self):
        return self.base_price * self.ticket_class.price_multiplier

    def __str__(self):
        return f"Ticket {self.id} for Seat {self.seat}"


class Promotion(models.Model):
    name = models.CharField(max_length=100)
    discount_percent = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def is_active(self):
        now_dt = now()
        return self.start_date <= now_dt <= self.end_date

    def __str__(self):
        return self.name


class Passenger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"


class Seat(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    row = models.PositiveIntegerField()
    seat_number = models.PositiveIntegerField()
    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ("flight", "row", "seat_number")

    def __str__(self):
        return f"Row {self.row} Seat {self.seat_number} on Flight {self.flight.id}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
    ]

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"


class ExtraService(models.Model):
    order = models.ForeignKey(
        Order, related_name="extraservices", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} (${self.price}) for Order {self.order.id}"


class FlightHistory(models.Model):
    flight = models.ForeignKey(
        Flight, related_name="flight_histories", on_delete=models.CASCADE
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    change_description = models.TextField()

    def __str__(self):
        return f"Change on Flight {self.flight.id} at {self.changed_at}"


class OrderHistory(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_histories", on_delete=models.CASCADE
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    change_description = models.TextField()

    def __str__(self):
        return f"Change on Order {self.order.id} at {self.changed_at}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for Flight {self.flight.id}"


class Airline(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    iata_code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.name


class RefundPolicy(models.Model):
    name = models.CharField(max_length=100)
    refundable = models.BooleanField(default=True)
    penalty_percent = models.PositiveIntegerField()
    valid_until = models.DurationField()

    def __str__(self):
        return self.name


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"
