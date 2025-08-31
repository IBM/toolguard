from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_payment_method_requirement_for_flight_changes import guard_payment_method_requirement_for_flight_changes
from airline.airline_types import *
from airline.i_airline import *

def test_flight_change_with_valid_credit_card():
    """
    Policy: "Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method."
    Example: "The user requests a flight change and provides a valid credit card from their profile, satisfying the policy requirement for payment method."
    """
    user = User(
        user_id="user123",
        name=Name(first_name="John", last_name="Doe"),
        address=Address(address1="123 Main St", address2=None, city="New York", country="USA", state="NY", zip="10001"),
        email="john.doe@example.com",
        dob="1980-01-01",
        payment_methods={
            "credit_card_123": CreditCard(source="credit_card", brand="visa", last_four="1234", id="credit_card_123")
        },
        saved_passengers=[],
        membership="gold",
        reservations=["resv001"]
    )
    reservation = Reservation(
        reservation_id="resv001",
        user_id="user123",
        origin="JFK",
        destination="LAX",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL123", origin="JFK", destination="LAX", date="2024-06-01", price=300)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv001" else None

    flights = [FlightInfo(flight_number="FL123", date="2024-06-02")]
    guard_payment_method_requirement_for_flight_changes(api, reservation_id="resv001", cabin="economy", flights=flights, payment_id="credit_card_123")

def test_flight_change_without_payment_method():
    """
    Policy: "Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method."
    Example: "A user attempts to change flights in a reservation without providing any valid payment information such as a gift card or credit card linked to their profile, which contravenes the policy."
    """
    user = User(
        user_id="user123",
        name=Name(first_name="John", last_name="Doe"),
        address=Address(address1="123 Main St", address2=None, city="New York", country="USA", state="NY", zip="10001"),
        email="john.doe@example.com",
        dob="1980-01-01",
        payment_methods={},
        saved_passengers=[],
        membership="gold",
        reservations=["resv001"]
    )
    reservation = Reservation(
        reservation_id="resv001",
        user_id="user123",
        origin="JFK",
        destination="LAX",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL123", origin="JFK", destination="LAX", date="2024-06-01", price=300)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv001" else None

    flights = [FlightInfo(flight_number="FL123", date="2024-06-02")]
    with pytest.raises(PolicyViolationException):
        guard_payment_method_requirement_for_flight_changes(api, reservation_id="resv001", cabin="economy", flights=flights, payment_id="")

def test_flight_change_with_certificate_only():
    """
    Policy: "Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method."
    Example: "A flight update process begins with the user providing only a certificate as payment, despite the requirement for a gift card or credit card."
    """
    user = User(
        user_id="user123",
        name=Name(first_name="John", last_name="Doe"),
        address=Address(address1="123 Main St", address2=None, city="New York", country="USA", state="NY", zip="10001"),
        email="john.doe@example.com",
        dob="1980-01-01",
        payment_methods={
            "certificate_123": Certificate(source="certificate", amount=100.0, id="certificate_123")
        },
        saved_passengers=[],
        membership="gold",
        reservations=["resv001"]
    )
    reservation = Reservation(
        reservation_id="resv001",
        user_id="user123",
        origin="JFK",
        destination="LAX",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL123", origin="JFK", destination="LAX", date="2024-06-01", price=300)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv001" else None

    flights = [FlightInfo(flight_number="FL123", date="2024-06-02")]
    with pytest.raises(PolicyViolationException):
        guard_payment_method_requirement_for_flight_changes(api, reservation_id="resv001", cabin="economy", flights=flights, payment_id="certificate_123")