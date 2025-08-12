from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_consistency_across_flight_segments import guard_consistency_across_flight_segments
from airline.i_airline import *
from airline.airline_types import *
from datetime import datetime, timedelta

class TestGuardConsistencyAcrossFlightSegments:

    def test_successful_update_with_all_flights_included(self):
        """
        Policy: "When updating a reservation, all flight segments must be included in the list of flights provided, regardless of whether they have been altered or not."
        Example: "A user's round-trip reservation is successfully updated with all flights listed, including the unchanged return flight segment, adhering to the policy requirement."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        api = MagicMock(spec=I_Airline)
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[
                ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK"),
                ReservationFlight(flight_number="HAT002", date="2024-05-08", price=300, origin="JFK", destination="SFO")
            ],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=600)],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        flights = [
            FlightInfo(flight_number="HAT001", date="2024-05-01"),
            FlightInfo(flight_number="HAT002", date="2024-05-08")
        ]
        guard_consistency_across_flight_segments(history, api, "ZFA04Y", "economy", flights, "credit_card_7815826")

    def test_update_with_missing_flight_segments(self):
        """
        Policy: "When updating a reservation, all flight segments must be included in the list of flights provided, regardless of whether they have been altered or not."
        Example: "A user attempts to update their reservation but only includes the altered flight segment in the flights array, omitting the unchanged flight segments."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        api = MagicMock(spec=I_Airline)
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[
                ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK"),
                ReservationFlight(flight_number="HAT002", date="2024-05-08", price=300, origin="JFK", destination="SFO")
            ],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=600)],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        flights = [
            FlightInfo(flight_number="HAT001", date="2024-05-01")
        ]
        with pytest.raises(PolicyViolationException):
            guard_consistency_across_flight_segments(history, api, "ZFA04Y", "economy", flights, "credit_card_7815826")
