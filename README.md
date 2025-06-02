# # ✈️ Airline Booking System

This is a Django-based airline booking and management system that allows users to search for flights, book tickets, manage airplanes and routes, assign crews, process payments, and more.

## 🚀 Features

- Manage **Countries**, **Cities**, **Airports**, and **Routes**
- Define **Airplanes** and **Airplane Types**
- Create **Flights** with automatic **Seat** generation
- Support for **Crew assignment**, **Ticket Classes**, and **Extra Services**
- Handle **Orders**, **Tickets**, **Payments**, and **Refund Policies**
- Track **Flight History** and **Order Changes**
- Enable **User Reviews** and **Notifications**
- Apply **Promotions** and manage **Airlines**

---

## 🧱 Model Overview

| Model                | Description |
|----------------------|-------------|
| `Country`, `City`    | Geographic hierarchy |
| `Airport`            | Airport information linked to cities |
| `Route`              | Source-destination mapping with distance |
| `Airplane`, `AirplaneType` | Aircraft specs and types |
| `Flight`             | Scheduled route with airplane, crew, and dynamic seat generation |
| `Crew`               | Crew members with first and last names |
| `Seat`               | Auto-generated seat data (aisle/window logic included) |
| `Ticket`             | Booking record with seat, order, and price logic |
| `TicketClass`        | Class of ticket (e.g., Economy, Business) with price multiplier |
| `ExtraService`       | Additional services like meals or luggage |
| `ExtraServicePrice`  | Service pricing per ticket class |
| `Order`              | Collection of tickets with extra services |
| `Passenger`          | Passenger profile with phone and passport info |
| `Payment`            | Payment info with status and date |
| `Review`             | User-submitted reviews of flights |
| `FlightHistory`, `OrderHistory` | Tracks changes to flights and orders |
| `Airline`            | Airline companies with IATA codes |
| `RefundPolicy`       | Refund rules including penalty and validity |
| `Notification`       | Alerts for users (read/unread tracking) |

---

## ⚙️ Key Business Logic

- **Dynamic Seat Creation**: When a flight is saved, seats are auto-generated based on airplane layout.
- **Ticket Pricing**: Calculated using route distance and ticket class multiplier.
- **Validation**: Clean methods enforce logical correctness (e.g. valid routes, correct seat numbers).
- **Seat Classification**: Logic distinguishes window and aisle seats depending on airplane layout.
- **Order Pricing**: Combines all ticket and extra service prices.
- **Promotions**: Time-limited discounts on orders or services.
- **Change Logs**: Historical tracking of flight and order modifications.

---

## 🛠️ Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/airline-booking-system.git
cd airline-booking-system
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/scripts/activate # For Mac
venv/scripts/Activate #For Windows
```
3. Install dependencies:

```bash
pip install -r requirements.txt
```
4. Set up environment variables
```bash
Copy the sample environment file and update it with your settings:
cp env.sample .env
Then edit .env and fill in the required variables (e.g., SECRET_KEY, DEBUG, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, etc.).

⚠️ Important: If you're using Docker for PostgreSQL, set POSTGRES_HOST to the Docker service name (e.g., db from docker-compose.yml)
```

5. Start the PostgresSQL container
``` bash
docker-compose up -d db
```

6. Apply database migrations
```bash 
python manage.py migrate
```


## TECHNOLOGIES USED

Python 3

Django

Django REST Framework

PostgreSQL

Docker & Docker Compose

Pillow (for image handling)