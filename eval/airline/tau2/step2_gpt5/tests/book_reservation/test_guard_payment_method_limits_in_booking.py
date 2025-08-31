from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_payment_method_limits_in_booking import guard_payment_method_limits_in_booking
from airline.i_airline import *
from airline.airline_types import *

def test_compliant_one_cert_one_card_two_gift():
    """
    Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
    Example: "A reservation where the user uses one travel certificate, one credit card, and two gift cards, adhering to the payment method limits."
    """
    user = User(
        user_id="user123",
        name=Name(first_name="Sara", last_name="Doe"),
        address=Address(address1="123 Main St", address2=None, city="City", country="Country", state="State", zip="12345"),
        email="sara@example.com",
        dob="1990-01-01",
        payment_methods={},
        saved_passengers=[],
        membership="gold",
        reservations=[]
    )

    api = MagicMock(spec=I_Airline)
    api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None

    flights = [FlightInfo(flight_number="FL123", date="2024-06-01")]
    passengers = [Passenger(first_name="John", last_name="Smith", dob="1985-05-05")]
    payment_methods = [
        Certificate(source="certificate", id="cert1", amount=100.0),
        CreditCard(source="credit_card", id="cc1", brand="visa", last_four="1234"),
        GiftCard(source="gift_card", id="gc1", amount=50.0),
        GiftCard(source="gift_card", id="gc2", amount=30.0)
    ]

    guard_payment_method_limits_in_booking(api, "user123", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")

def test_violation_two_cert_four_gift():
    """
    Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
    Example: "A user attempts to book a reservation using two travel certificates and four gift cards, exceeding the policy limits for each of these payment types."
    """
    user = User(
        user_id="user123",
        name=Name(first_name="Sara", last_name="Doe"),
        address=Address(address1="123 Main St", address2=None, city="City", country="Country", state="State", zip="12345"),
        email="sara@example.com",
        dob="1990-01-01",
        payment_methods={},
        saved_passengers=[],
        membership="gold",
        reservations=[]
    )

    api = MagicMock(spec=I_Airline)
    api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None

    flights = [FlightInfo(flight_number="FL123", date="2024-06-01")]
    passengers = [Passenger(first_name="John", last_name="Smith", dob="1985-05-05")]
    payment_methods = [
        Certificate(source="certificate", id="cert1", amount=100.0),
        Certificate(source="certificate", id="cert2", amount=150.0),
        GiftCard(source="gift_card", id="gc1", amount=50.0),
        GiftCard(source="gift_card", id="gc2", amount=30.0),
        GiftCard(source="gift_card", id="gc3", amount=20.0),
        GiftCard(source="gift_card", id="gc4", amount=10.0)
    ]

    with pytest.raises(PolicyViolationException):
        guard_payment_method_limits_in_booking(api, "user123", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")

def test_violation_three_credit_cards():
    """
    Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
    Example: "A reservation is attempted using a combination of three credit cards, violating the policy as only one credit card is permitted per reservation."
    """
    user = User(
        user_id="user123",
        name=Name(first_name="Sara", last_name="Doe"),
        address=Address(address1="123 Main St", address2=None, city="City", country="Country", state="State", zip="12345"),
        email="sara@example.com",
        dob="1990-01-01",
        payment_methods={},
        saved_passengers=[],
        membership="gold",
        reservations=[]
    )

    api = MagicMock(spec=I_Airline)
    api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None

    flights = [FlightInfo(flight_number="FL123", date="2024-06-01")]
    passengers = [Passenger(first_name="John", last_name="Smith", dob="1985-05-05")]
    payment_methods = [
        CreditCard(source="credit_card", id="cc1", brand="visa", last_four="1234"),
        CreditCard(source="credit_card", id="cc2", brand="mastercard", last_four="5678"),
        CreditCard(source="credit_card", id="cc3", brand="amex", last_four="9012")
    ]

    with pytest.raises(PolicyViolationException):
        guard_payment_method_limits_in_booking(api, "user123", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")