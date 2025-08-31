from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.cancel_reservation.guard_strict_cancellation_rules_enforcement import guard_strict_cancellation_rules_enforcement
from airline.airline_types import *
from airline.i_airline import *


def test_cancel_within_24_hours():
    """ 
    Policy: "All reservations can be cancelled within 24 hours of booking"
    Example: "An agent checks that a reservation was booked less than 24 hours ago and cancels it accordingly, ensuring compliance with the policy."
    """
    api = MagicMock(spec=I_Airline)
    created_at = (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S")
    reservation = Reservation(
        reservation_id="ABC123",
        user_id="user1",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[],
        passengers=[],
        payment_history=[],
        created_at=created_at,
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ABC123" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(status="available", available_seats={"business": 1, "economy": 1, "basic_economy": 1}, prices={"business": 1000, "economy": 500, "basic_economy": 300})

    guard_strict_cancellation_rules_enforcement(api, reservation_id="ABC123")


def test_cancel_airline_cancelled_flight():
    """ 
    Policy: "All reservations can be cancelled if the airline cancelled the flight"
    Example: "An agent verifies that a flight was cancelled by the airline before executing cancellation to comply with policy rules."
    """
    api = MagicMock(spec=I_Airline)
    created_at = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")
    reservation = Reservation(
        reservation_id="DEF456",
        user_id="user2",
        origin="SFO",
        destination="JFK",
        flight_type="one_way",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL123", origin="SFO", destination="JFK", date="2024-06-01", price=500)],
        passengers=[],
        payment_history=[],
        created_at=created_at,
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "DEF456" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusCancelled(status="cancelled") if fn == "FL123" else None

    guard_strict_cancellation_rules_enforcement(api, reservation_id="DEF456")


def test_violation_no_policy_check():
    """ 
    Policy: Must check airline cancellation or within 24 hours before cancelling
    Example: "An agent attempts to cancel a reservation without checking if the airline has cancelled the flight or if it's within the 24-hour booking period, violating policy conditions."
    """
    api = MagicMock(spec=I_Airline)
    created_at = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
    reservation = Reservation(
        reservation_id="GHI789",
        user_id="user3",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL456", origin="SFO", destination="JFK", date="2024-06-01", price=500)],
        passengers=[],
        payment_history=[],
        created_at=created_at,
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "GHI789" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(status="available", available_seats={"business": 1, "economy": 1, "basic_economy": 1}, prices={"business": 1000, "economy": 500, "basic_economy": 300})

    with pytest.raises(PolicyViolationException):
        guard_strict_cancellation_rules_enforcement(api, reservation_id="GHI789")