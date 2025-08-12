from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_explicit_user_confirmation_required import guard_explicit_user_confirmation_required
from airline.i_airline import *
from datetime import datetime, timedelta

class TestGuardExplicitUserConfirmationRequired:

    def test_compliance_user_confirmation_received(self):
        """
        Policy: "Explicit User Confirmation Required"
        Example: "The agent presents the updated flight itinerary, cabin class changes, and passenger adjustments in detail and waits for the user to reply 'yes' before proceeding, ensuring compliance with the required user confirmation."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = True  # Mock that user confirmed with 'yes'

        # Mock other tools function return values
        reservation = Reservation(reservation_id="ZFA04Y", user_id="sara_doe_496", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-05-01", price=300)], passengers=[], payment_history=[], created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"), total_baggages=2, nonfree_baggages=1, insurance="yes", status=None)
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="gold", reservations=["ZFA04Y"])

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        # Invoke function under test.
        guard_explicit_user_confirmation_required(history, api, reservation_id="ZFA04Y", cabin="economy", flights=[{"flight_number": "HAT001", "date": "2024-05-01"}], payment_id="credit_card_7815826")

    def test_violation_no_user_confirmation(self):
        """
        Policy: "Explicit User Confirmation Required"
        Example: "An agent updates the flight details of a reservation without asking the user for confirmation, proceeding with changes based on assumed preferences, which violates the requirement for explicit user consent."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = False  # Mock that user did not confirm with 'yes'

        # Mock other tools function return values
        reservation = Reservation(reservation_id="ZFA04Y", user_id="sara_doe_496", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-05-01", price=300)], passengers=[], payment_history=[], created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"), total_baggages=2, nonfree_baggages=1, insurance="yes", status=None)
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="gold", reservations=["ZFA04Y"])

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        # Invoke function under test.
        with pytest.raises(PolicyViolationException):
            guard_explicit_user_confirmation_required(history, api, reservation_id="ZFA04Y", cabin="economy", flights=[{"flight_number": "HAT001", "date": "2024-05-01"}], payment_id="credit_card_7815826")