from unittest.mock import MagicMock
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_flight_passenger_limit_for_booking import guard_flight_passenger_limit_for_booking
from airline.airline_types import *
from airline.i_airline import *

def test_booking_three_passengers_same_itinerary():
    """
    Policy: A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin.
    Example: Booking for three passengers: John Doe, Jane Smith, and Alex Murphy, all flying economy class from JFK to SFO with identical flight segments.
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT001", date="2024-06-01")]
    passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alex", last_name="Murphy", dob="1992-07-07")
    ]
    payment_methods = [Payment(payment_id="pay123", amount=500)]

    try:
        guard_flight_passenger_limit_for_booking(api, "user123", "JFK", "SFO", "one_way", "economy", flights, passengers, payment_methods, 2, 1, "no")
    except PolicyViolationException:
        pytest.fail("Test failed: Expected compliance but got PolicyViolationException")

def test_booking_six_passengers_exceeds_limit():
    """
    Policy: A flight reservation can have at most five passengers.
    Example: A reservation is attempted for six passengers: John Doe, Jane Smith, Alex Murphy, Ella Brown, Chris Davis, and Emily White.
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT002", date="2024-06-01")]
    passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alex", last_name="Murphy", dob="1992-07-07"),
        Passenger(first_name="Ella", last_name="Brown", dob="1991-03-03"),
        Passenger(first_name="Chris", last_name="Davis", dob="1988-08-08"),
        Passenger(first_name="Emily", last_name="White", dob="1993-09-09")
    ]
    payment_methods = [Payment(payment_id="pay124", amount=1000)]

    with pytest.raises(PolicyViolationException):
        guard_flight_passenger_limit_for_booking(api, "user124", "SFO", "JFK", "one_way", "economy", flights, passengers, payment_methods, 3, 2, "yes")

def test_booking_different_cabin_classes():
    """
    Policy: All passengers must fly the same flights in the same cabin.
    Example: Four passengers with John flying business class and others flying economy.
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT003", date="2024-06-01")]
    passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alex", last_name="Murphy", dob="1992-07-07"),
        Passenger(first_name="Ella", last_name="Brown", dob="1991-03-03")
    ]
    payment_methods = [Payment(payment_id="pay125", amount=800)]

    with pytest.raises(PolicyViolationException):
        guard_flight_passenger_limit_for_booking(api, "user125", "JFK", "LAX", "one_way", "business", flights, passengers, payment_methods, 1, 0, "no")

def test_booking_different_flight_itineraries():
    """
    Policy: All passengers must fly the same flights in the same cabin.
    Example: Three passengers with different flight itineraries.
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT004", date="2024-06-01"), FlightInfo(flight_number="HAT005", date="2024-06-02")]
    passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alex", last_name="Murphy", dob="1992-07-07")
    ]
    payment_methods = [Payment(payment_id="pay126", amount=900)]

    with pytest.raises(PolicyViolationException):
        guard_flight_passenger_limit_for_booking(api, "user126", "JFK", "SFO", "one_way", "economy", flights, passengers, payment_methods, 2, 1, "yes")