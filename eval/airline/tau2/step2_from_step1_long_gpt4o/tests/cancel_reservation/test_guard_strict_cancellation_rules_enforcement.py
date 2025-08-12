from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.cancel_reservation.guard_strict_cancellation_rules_enforcement import guard_strict_cancellation_rules_enforcement
from airline.i_airline import *
from datetime import datetime, timedelta

class TestGuardStrictCancellationRulesEnforcement:

    def test_cancel_within_24_hours_of_booking(self):
        """
        Policy: "An agent checks that a reservation was booked less than 24 hours ago and cancels it accordingly, ensuring compliance with the policy."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[],
            created_at=(datetime.now() - timedelta(hours=23)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        guard_strict_cancellation_rules_enforcement(history, api, "ZFA04Y")

    def test_cancelled_by_airline(self):
        """
        Policy: "An agent verifies that a flight was cancelled by the airline before executing cancellation to comply with policy rules."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[],
            created_at=(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.get_flight_status.side_effect = lambda flight_number, date: "cancelled" if flight_number == "HAT001" and date == "2024-05-01" else "available"

        guard_strict_cancellation_rules_enforcement(history, api, "ZFA04Y")

    def test_violation_no_check_on_airline_cancellation(self):
        """
        Policy: "An agent attempts to cancel a reservation without checking if the airline has cancelled the flight or if it's within the 24-hour booking period, violating policy conditions."
        """
        history = MagicMock()
        history.ask_bool.return_value = False

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[],
            created_at=(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.get_flight_status.side_effect = lambda flight_number, date: "available" if flight_number == "HAT001" and date == "2024-05-01" else "cancelled"

        with pytest.raises(PolicyViolationException):
            guard_strict_cancellation_rules_enforcement(history, api, "ZFA04Y")

    def test_violation_partial_cancellation_attempt(self):
        """
        Policy: "The agent proceeds to cancel part of a reservation even when some segments have already been flown, which breaches the rule against partial cancellations."
        """
        history = MagicMock()
        history.ask_bool.return_value = False

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[],
            created_at=(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.get_flight_status.side_effect = lambda flight_number, date: "flying" if flight_number == "HAT001" and date == "2024-05-01" else "available"

        with pytest.raises(PolicyViolationException):
            guard_strict_cancellation_rules_enforcement(history, api, "ZFA04Y")
