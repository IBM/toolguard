from unittest.mock import MagicMock
import pytest
from datetime import datetime
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_cabin_change_payment_requirement import guard_cabin_change_payment_requirement
from airline.airline_types import *
from airline.i_airline import *

def test_change_entire_reservation_cabin():
    """
    Policy: Ensure a uniform cabin class change across all flights within the reservation and payment for the fare difference.
    Example: A user changes the entire reservation's cabin class from economy to business, ensuring all flight segments are included and provides payment details to cover the fare difference.
    """
    
    # Mock reservation details
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[
            ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-06-01", price=200),
            ReservationFlight(flight_number="HAT002", origin="JFK", destination="SFO", date="2024-06-10", price=200)
        ],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )

    # Mock API
    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(
        status="available",
        available_seats={"business": 5, "economy": 5, "basic_economy": 5},
        prices={"business": 400, "economy": 200, "basic_economy": 100}
    ) if (fn, date) in [("HAT001", "2024-06-01"), ("HAT002", "2024-06-10")] else None

    flights = [
        FlightInfo(flight_number="HAT001", date="2024-06-01"),
        FlightInfo(flight_number="HAT002", date="2024-06-10")
    ]

    guard_cabin_change_payment_requirement(api, "ZFA04Y", "business", flights, "credit_card_123")

def test_change_only_one_segment_raises():
    """
    Policy: Uniform cabin class change required across all flights.
    Example: A user attempts to change only one segment of their reservation from economy to business class without updating the cabin class for the entire reservation.
    """
    
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[
            ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-06-01", price=200),
            ReservationFlight(flight_number="HAT002", origin="JFK", destination="SFO", date="2024-06-10", price=200)
        ],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )

    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(
        status="available",
        available_seats={"business": 5, "economy": 5, "basic_economy": 5},
        prices={"business": 400, "economy": 200, "basic_economy": 100}
    ) if (fn, date) in [("HAT001", "2024-06-01"), ("HAT002", "2024-06-10")] else None

    flights = [
        FlightInfo(flight_number="HAT001", date="2024-06-01")
    ]

    with pytest.raises(PolicyViolationException):
        guard_cabin_change_payment_requirement(api, "ZFA04Y", "business", flights, "credit_card_123")

def test_mixed_cabin_classes_raises():
    """
    Policy: Uniform cabin class change required across all flights.
    Example: A user updates their reservation to have mixed cabin classes, changing one flight to economy and another to business class.
    """
    
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[
            ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-06-01", price=200),
            ReservationFlight(flight_number="HAT002", origin="JFK", destination="SFO", date="2024-06-10", price=200)
        ],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )

    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(
        status="available",
        available_seats={"business": 5, "economy": 5, "basic_economy": 5},
        prices={"business": 400, "economy": 200, "basic_economy": 100}
    ) if (fn, date) in [("HAT001", "2024-06-01"), ("HAT002", "2024-06-10")] else None

    flights = [
        FlightInfo(flight_number="HAT001", date="2024-06-01"),
        FlightInfo(flight_number="HAT002", date="2024-06-10")
    ]

    with pytest.raises(PolicyViolationException):
        guard_cabin_change_payment_requirement(api, "ZFA04Y", "economy", flights, "credit_card_123")