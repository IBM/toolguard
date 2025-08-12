from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_cabin_change_payment_requirement import guard_cabin_change_payment_requirement
from airline.i_airline import *
from datetime import datetime, timedelta

class TestGuardCabinChangePaymentRequirement:

    def test_compliance_change_entire_reservation_cabin(self):
        """
        Policy: "ToolX can be used to modify a reservation's cabin class. Ensure a uniform cabin class change across all flights within the reservation. Make sure the user pays the fare difference between the current cabin class and the new cabin class for the entire reservation as partial changes are disallowed."
        Example: "A user changes the entire reservation's cabin class from economy to business, ensuring all flight segments are included in the updated reservation request and provides payment details to cover the fare difference, fully complying with the policy."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        api = MagicMock(spec=I_Airline)
        reservation = Reservation(reservation_id="ZFA04Y", user_id="user123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=200, origin="SFO", destination="JFK")], passengers=[], payment_history=[], created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"), total_baggages=0, nonfree_baggages=0, insurance="no", status=None)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        guard_cabin_change_payment_requirement(history, api, reservation_id="ZFA04Y", cabin="business", flights=[FlightInfo(flight_number="HAT001", date="2024-05-01")], payment_id="credit_card_7815826")

    def test_violation_change_single_segment_cabin(self):
        """
        Policy: "ToolX can be used to modify a reservation's cabin class. Ensure a uniform cabin class change across all flights within the reservation. Make sure the user pays the fare difference between the current cabin class and the new cabin class for the entire reservation as partial changes are disallowed."
        Example: "A user attempts to change only one segment of their reservation from economy to business class without updating the cabin class for the entire reservation, violating the required uniform cabin change."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        api = MagicMock(spec=I_Airline)
        reservation = Reservation(reservation_id="ZFA04Y", user_id="user123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=200, origin="SFO", destination="JFK")], passengers=[], payment_history=[], created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"), total_baggages=0, nonfree_baggages=0, insurance="no", status=None)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_cabin_change_payment_requirement(history, api, reservation_id="ZFA04Y", cabin="business", flights=[FlightInfo(flight_number="HAT001", date="2024-05-01")], payment_id="credit_card_7815826")
