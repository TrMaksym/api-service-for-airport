from unittest import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from flights.models import Country, City, Airport, Route, Airplane, AirplaneType, Flight, Crew, Order, Payment, \
    TicketClass, Seat
from uuid import uuid4

User = get_user_model()


class BaseTestSetup(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            email=f"admin_{uuid4()}@test.com", password="adminpass"
        )
        cls.user = User.objects.create_user(
            email=f"user_{uuid4()}@test.com", password="userpass"
        )
        cls.country = Country.objects.create(country="TestCountry")
        cls.city = City.objects.create(country=cls.country, name="TestCity")
        cls.airport = Airport.objects.create(name="TestAirport", city=cls.city)


class CountryViewSetTests(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("flight:country-list")

    def test_list_countries_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_country_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"country": "NewCountry"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["country"], "NewCountry")

    def test_create_country_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {"country": "AnotherCountry"}
        response = self.client.post(self.url, data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_list_countries_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_countries_anonymous_forbidden(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_create_country_with_empty_name(self):
        self.client.force_authenticate(user=self.admin)
        data = {"country": ""}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("country", response.data)


class AirportViewSetTests(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("flight:airport-list")
        self.detail_url = lambda pk: reverse("flight:airport-detail", args=[pk])

    def test_list_airports(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_retrieve_airport(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.airport.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.airport.name)

    def test_create_airport_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "NewAirport", "city_id": self.city.pk}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "NewAirport")

    def test_create_airport_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "UserAirport", "city_id": self.city.pk}
        response = self.client.post(self.list_url, data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_update_airport_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "UpdatedAirport", "city_id": self.city.pk}
        response = self.client.put(self.detail_url(self.airport.pk), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "UpdatedAirport")

    def test_update_airport_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "UserUpdate", "city_id": self.city.pk}
        response = self.client.put(self.detail_url(self.airport.pk), data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_delete_airport_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url(self.airport.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_airport_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.airport.pk))
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_partial_update_airport_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "PartiallyUpdatedAirport"}
        response = self.client.patch(self.detail_url(self.airport.pk), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "PartiallyUpdatedAirport")

    def test_partial_update_airport_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "UserPartialUpdate"}
        response = self.client.patch(self.detail_url(self.airport.pk), data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_list_airports_anonymous_forbidden(self):
        response = self.client.get(self.list_url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])


class RouteViewSetTests(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.airport2 = Airport.objects.create(name="Airport2", city=self.city)
        self.list_url = reverse("flight:route-list")
        self.detail_url = lambda pk: reverse("flight:route-detail", args=[pk])

    def test_list_routes(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_route_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "source_id": self.airport.pk,
            "destination_id": self.airport2.pk,
            "distance": 1000,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["distance"], 1000)

    def test_create_route_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "source_id": self.airport.pk,
            "destination_id": self.airport2.pk,
            "distance": 500,
        }
        response = self.client.post(self.list_url, data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_update_route_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        route = Route.objects.create(source=self.airport, destination=self.airport2, distance=800)
        data = {
            "source_id": self.airport.pk,
            "destination_id": self.airport2.pk,
            "distance": 1200,
        }
        response = self.client.put(self.detail_url(route.pk), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["distance"], 1200)

    def test_update_route_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        route = Route.objects.create(source=self.airport, destination=self.airport2, distance=800)
        data = {
            "source_id": self.airport.pk,
            "destination_id": self.airport2.pk,
            "distance": 1200,
        }
        response = self.client.put(self.detail_url(route.pk), data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_delete_route_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        route = Route.objects.create(source=self.airport, destination=self.airport2, distance=800)
        response = self.client.delete(self.detail_url(route.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_route_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        route = Route.objects.create(source=self.airport, destination=self.airport2, distance=800)
        response = self.client.delete(self.detail_url(route.pk))
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_create_route_with_same_source_and_destination(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "source_id": self.airport.pk,
            "destination_id": self.airport.pk,
            "distance": 100,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)


class AirplaneViewSetTests(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("flight:airplane-list")
        self.airplane_type = AirplaneType.objects.create(name="Commercial")
        self.airplane = Airplane.objects.create(
            name="Boeing 747",
            rows=20,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

    def test_list_airplanes(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_airplane_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "Airbus A320",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type_id": self.airplane_type.pk,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Airbus A320")

    def test_create_airplane_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Cessna 172",
            "rows": 15,
            "seats_in_row": 4,
            "airplane_type_id": self.airplane_type.pk,
        }
        response = self.client.post(self.list_url, data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_update_airplane_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "Boeing 747 Updated",
            "rows": 22,
            "seats_in_row": 9,
            "airplane_type_id": self.airplane_type.pk,
        }
        url = reverse("flight:airplane-detail", args=[self.airplane.pk])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Boeing 747 Updated")

    def test_update_airplane_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Boeing 747",
            "rows": 22,
            "seats_in_row": 6,
            "airplane_type_id": self.airplane_type.pk,
        }
        url = reverse("flight:airplane-detail", args=[self.airplane.pk])
        response = self.client.put(url, data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_delete_airplane_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("flight:airplane-detail", args=[self.airplane.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_airplane_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("flight:airplane-detail", args=[self.airplane.pk])
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])


class FlightViewSetTests(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = AirplaneType.objects.create(name="Passenger")
        self.airplane = Airplane.objects.create(
            name="Airbus A380",
            rows=30,
            seats_in_row=10,
            airplane_type=self.airplane_type,
        )
        self.airport2 = Airport.objects.create(name="Airport2", city=self.city)
        self.route = Route.objects.create(source=self.airport, destination=self.airport2, distance=1500)
        self.list_url = reverse("flight:flight-list")

    def test_list_flights(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_flight_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "route_id": self.route.pk,
            "airplane_id": self.airplane.pk,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=2)).isoformat(),
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_flight_invalid_times(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "route_id": self.route.pk,
            "airplane_id": self.airplane.pk,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() - timezone.timedelta(hours=1)).isoformat(),
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_flight_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "route_id": self.route.pk,
            "airplane_id": self.airplane.pk,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=2)).isoformat(),
        }
        response = self.client.post(self.list_url, data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_update_flight_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
        )
        data = {
            "route_id": self.route.pk,
            "airplane_id": self.airplane.pk,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=3)).isoformat(),
        }
        url = reverse("flight:flight-detail", args=[flight.pk])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_flight_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
        )
        url = reverse("flight:flight-detail", args=[flight.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CrewViewSetTests(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("flight:crew-list")
        self.airplane_type = AirplaneType.objects.create(name="Cargo")
        self.airplane = Airplane.objects.create(
            name="Cargo Plane",
            rows=10,
            seats_in_row=4,
            airplane_type=self.airplane_type,
        )
        self.crew = Crew.objects.create(
            first_name="John", last_name="Doe",
        )

    def test_list_crew(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_crew_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "first_name": "Alice",
            "last_name": "Smith",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Alice")

    def test_create_crew_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "first_name": "Bob",
            "last_name": "Brown",
        }
        response = self.client.post(self.list_url, data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_update_crew_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "first_name": "John",
            "last_name": "Updated",
        }
        url = reverse("flight:crew-detail", args=[self.crew.pk])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["last_name"], "Updated")

    def test_delete_crew_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("flight:crew-detail", args=[self.crew.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_crew_missing_first_name(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "last_name": "NoFirstName",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)


class TestOrderQuerysetUserRestriction(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        ticket_class = TicketClass.objects.create(name="Economy")

        Order.objects.create(user=self.user, id=1, ticket_class=ticket_class)
        other_user = User.objects.create_user(email=f"user2_{uuid4()}@test.com", password="pass")
        Order.objects.create(user=other_user, id=2, ticket_class=ticket_class)

    def test_order_queryset_user_restriction(self):
        response = self.client.get(reverse("flight:order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(o["user"] == self.user.username for o in response.data))


class TestPaymentQuerysetUserFilter(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        ticket_class = TicketClass.objects.create(name="Economy")

        order1 = Order.objects.create(user=self.user, ticket_class=ticket_class)
        other_user = User.objects.create_user(email=f"user3_{uuid4()}@test.com", password="pass")
        order2 = Order.objects.create(user=other_user, ticket_class=ticket_class)

        Payment.objects.create(order=order1, amount=100)
        Payment.objects.create(order=order2, amount=200)

    def test_payment_queryset_user_filter(self):
        response = self.client.get(reverse("flight:payment-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for payment in response.data:
            order_id = payment["order"]
            order = Order.objects.get(id=order_id)
            self.assertEqual(order.user.username, self.user.username)


class TestGetSerializerClassVariousActions(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")

        self.airplane = Airplane.objects.create(
            name="Plane1",
            rows=30,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )

    def test_get_serializer_class_various_actions(self):
        urls = {
            "list": reverse("flight:airplane-list"),
            "retrieve": reverse("flight:airplane-detail", args=[self.airplane.id]),
            "upload_image": reverse("flight:airplane-upload-image", args=[self.airplane.id]),
        }

        response = self.client.get(urls["list"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(urls["retrieve"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(urls["upload_image"])
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TicketClassViewSetTests(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("flight:ticketclass-list")

    def test_list_ticket_classes(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_ticket_class_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Business"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Business")

    def test_create_ticket_class_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Economy Plus"}
        response = self.client.post(self.list_url, data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

class TicketViewSetTests(BaseTestSetup):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.ticket_class = TicketClass.objects.create(name="Economy")
        self.list_url = reverse("flight:ticket-list")

        airplane_type = AirplaneType.objects.create(name="Passenger")
        airplane = Airplane.objects.create(name="TestPlane", rows=20, seats_in_row=6, airplane_type=airplane_type)
        airport2 = Airport.objects.create(name="Airport2", city=self.city)
        route = Route.objects.create(source=self.airport, destination=airport2, distance=1000)
        self.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
        )
        self.order = Order.objects.create(user=self.user, ticket_class=self.ticket_class)

    def test_list_tickets(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_ticket_as_user(self):
        self.client.force_authenticate(user=self.user)

        seat, created = Seat.objects.get_or_create(flight=self.flight, row=12, seat_number=1)

        data = {
            "order": self.order.pk,
            "flight": self.flight.pk,
            "seat": seat.pk,
            "ticket_class": self.ticket_class.pk,
            "price": "150.00",
        }
        response = self.client.post(self.list_url, data)

        print(response.status_code)
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("seat_number"), 1)
