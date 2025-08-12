from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_cannot_modify_basic_economy_flights import guard_cannot_modify_basic_economy_flights
from airline.i_airline import *
from datetime import datetime, timedelta

class TestGuardCannotModifyBasicEconomyFlights:

    def test_modify_basic_economy_flight(self):
        """
        Policy: "Basic economy flights in a reservation cannot be modified at all."
        Example: "A user attempts to change a reservation with basic economy flights by providing a new itinerary with updated origin and destination details, violating the restriction on modifying basic economy flights."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API tool function return values
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="basic_economy",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK")],
            passengers=[],
            payment_history=[],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=1,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test.
        with pytest.raises(PolicyViolationException):
            guard_cannot_modify_basic_economy_flights(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                cabin="basic_economy",
                flights=[{"flight_number": "HAT002", "date": "2024-05-02", "origin": "SFO", "destination": "JFK"}],
                payment_id="credit_card_7815826"
            )

    def test_modify_business_reservation_compliance(self):
        """
        Policy: "Modifications are allowed for non-basic economy reservations but must not change the origin, destination, or trip type."
        Example: "An agent successfully updates a 'business' reservation by changing the flight times, keeping the same origin 'SFO' and destination 'JFK' without altering the trip type from 'round_trip', ensuring compliance with the policy."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API tool function return values
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="business",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK")],
            passengers=[],
            payment_history=[],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=1,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test.
        try:
            guard_cannot_modify_basic_economy_flights(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                cabin="business",
                flights=[{"flight_number": "HAT001", "date": "2024-05-01", "origin": "SFO", "destination": "JFK"}],
                payment_id="credit_card_7815826"
            )
        except PolicyViolationException:
            pytest.fail("Business reservation modification failed unexpectedly.")

    # Additional tests for other compliance and violation examples can be added similarly.
