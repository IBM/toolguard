from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_passengers.guard_ensure_user_confirmation import guard_ensure_user_confirmation
from airline.i_airline import *
from airline.airline_types import *

class TestGuardEnsureUserConfirmation:
    
    def test_compliance_email_confirmation(self):
        """
        Policy: "Before using ToolX to update passenger information in the booking database, an airline agent must present the details of the changes to the user and obtain explicit confirmation ('yes') from them before proceeding."
        Example: "Before updating the passenger information for reservation 'ZFA04Y', the airline agent sends an email detailing the changes and receives a reply from the user confirming 'yes' before proceeding."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = True  # Mock that 'yes' is the answer to the confirmation question

        # Mock other tools function return values
        reservation = Reservation(reservation_id="ZFA04Y", user_id="user123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[], passengers=[], payment_history=[], created_at="2023-10-01T12:00:00", total_baggages=2, nonfree_baggages=1, insurance="yes", status=None)
        user = User(user_id="user123", name=Name(first_name="John", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"), email="john.doe@example.com", dob="1990-01-01", payment_methods={}, saved_passengers=[], membership="regular", reservations=["ZFA04Y"])

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user123" else None
        
        passengers = [Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")]

        # Invoke function under test.
        guard_ensure_user_confirmation(history, api, "ZFA04Y", passengers)

    def test_violation_no_confirmation(self):
        """
        Policy: "Before using ToolX to update passenger information in the booking database, an airline agent must present the details of the changes to the user and obtain explicit confirmation ('yes') from them before proceeding."
        Example: "An airline agent updates the passenger information for a reservation without displaying the changes to the user or obtaining explicit confirmation from them, violating the policy that requires a 'yes' confirmation before proceeding."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = False  # Mock that 'no' is the answer to the confirmation question

        # Mock other tools function return values
        reservation = Reservation(reservation_id="ZFA04Y", user_id="user123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[], passengers=[], payment_history=[], created_at="2023-10-01T12:00:00", total_baggages=2, nonfree_baggages=1, insurance="yes", status=None)
        user = User(user_id="user123", name=Name(first_name="John", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"), email="john.doe@example.com", dob="1990-01-01", payment_methods={}, saved_passengers=[], membership="regular", reservations=["ZFA04Y"])

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user123" else None
        
        passengers = [Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")]

        # Invoke function under test.
        with pytest.raises(PolicyViolationException):
            guard_ensure_user_confirmation(history, api, "ZFA04Y", passengers)
