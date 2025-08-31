from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_consistency_across_flight_segments import guard_consistency_across_flight_segments
from airline.airline_types import *
from airline.i_airline import *

class TestGuardConsistencyAcrossFlightSegments:

    def test_update_with_all_segments_included(self):
        """ 
        Policy: "When updating a reservation, all flight segments must be included in the list of flights provided, regardless of whether they have been altered or not."
        Example: "A user's round-trip reservation is successfully updated with all flights listed, including the unchanged return flight segment, adhering to the policy requirement."
        """
        
        # Mock reservation with two segments
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[
                ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-06-01", price=300),
                ReservationFlight(flight_number="HAT002", origin="JFK", destination="SFO", date="2024-06-10", price=320)
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

        flights = [
            FlightInfo(flight_number="HAT001", date="2024-06-01"),
            FlightInfo(flight_number="HAT002", date="2024-06-10")
        ]

        # Should not raise
        guard_consistency_across_flight_segments(api, reservation_id="ZFA04Y", cabin="economy", flights=flights, payment_id="credit_card_123")

    def test_update_with_only_altered_segment(self):
        """ 
        Policy: "When updating a reservation, all flight segments must be included in the list of flights provided, regardless of whether they have been altered or not."
        Example: "A user attempts to update their reservation but only includes the altered flight segment in the flights array, omitting the unchanged flight segments."
        """
        
        # Mock reservation with two segments
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[
                ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-06-01", price=300),
                ReservationFlight(flight_number="HAT002", origin="JFK", destination="SFO", date="2024-06-10", price=320)
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

        flights = [
            FlightInfo(flight_number="HAT001", date="2024-06-01")
        ]

        with pytest.raises(PolicyViolationException):
            guard_consistency_across_flight_segments(api, reservation_id="ZFA04Y", cabin="economy", flights=flights, payment_id="credit_card_123")

    def test_update_excludes_connecting_segments(self):
        """ 
        Policy: "When updating a reservation, all flight segments must be included in the list of flights provided, regardless of whether they have been altered or not."
        Example: "An agent updates the reservation for a flight change but mistakenly excludes connecting segments that were part of the same trip, leading to an incomplete submission."
        """
        
        # Mock reservation with three segments (one connection)
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="LHR",
            flight_type="one_way",
            cabin="business",
            flights=[
                ReservationFlight(flight_number="HAT100", origin="SFO", destination="JFK", date="2024-07-01", price=200),
                ReservationFlight(flight_number="HAT200", origin="JFK", destination="LHR", date="2024-07-02", price=500)
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

        flights = [
            FlightInfo(flight_number="HAT100", date="2024-07-01")
        ]

        with pytest.raises(PolicyViolationException):
            guard_consistency_across_flight_segments(api, reservation_id="ZFA04Y", cabin="business", flights=flights, payment_id="credit_card_123")

    def test_update_excludes_ancillary_service_segments(self):
        """ 
        Policy: "When updating a reservation, all flight segments must be included in the list of flights provided, regardless of whether they have been altered or not."
        Example: "During a reservation update involving a cabin class upgrade, the flights array only lists flights under the new cabin class, excluding previously booked ancillary services segments, violating the policy."
        """
        
        # Mock reservation with main flight and ancillary service segment
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="one_way",
            cabin="economy",
            flights=[
                ReservationFlight(flight_number="HAT300", origin="SFO", destination="JFK", date="2024-08-01", price=300),
                ReservationFlight(flight_number="ANC001", origin="JFK", destination="JFK", date="2024-08-01", price=50)
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

        flights = [
            FlightInfo(flight_number="HAT300", date="2024-08-01")
        ]

        with pytest.raises(PolicyViolationException):
            guard_consistency_across_flight_segments(api, reservation_id="ZFA04Y", cabin="business", flights=flights, payment_id="credit_card_123")