from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_user_confirmation_before_database_update import guard_user_confirmation_before_database_update
from airline.i_airline import *
from datetime import datetime, timedelta

class TestGuardUserConfirmationBeforeDatabaseUpdate:

    def test_compliance_example_emily_reservation_confirmation(self):
        """
        Policy: "Ensure that before using ToolX for database updates related to booking a reservation, changing flight details, passenger information, baggage edits, or cabin upgrades, you must present the details of these actions to the user and obtain a clear affirmative confirmation ('yes') from the user before proceeding."
        Example: "Before finalizing a new reservation for Emily, including flight details, passenger names, and baggage information, the system displays all changes to Emily and obtains her explicit 'yes' confirmation to proceed with the booking."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="emily_123", name=Name(first_name="Emily", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="New York", country="USA", state="NY", zip="10001"), email="emily@example.com", dob="1990-01-01", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "emily_123" else None

        flights = [FlightInfo(flight_number="FL123", date="2024-05-01")]
        passengers = [Passenger(first_name="Emily", last_name="Doe", dob="1990-01-01")]
        payment_methods = [Payment(payment_id="pay_001", amount=200)]

        guard_user_confirmation_before_database_update(history, api, "emily_123", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")

    def test_violation_example_john_no_confirmation(self):
        """
        Policy: "Ensure that before using ToolX for database updates related to booking a reservation, changing flight details, passenger information, baggage edits, or cabin upgrades, you must present the details of these actions to the user and obtain a clear affirmative confirmation ('yes') from the user before proceeding."
        Example: "The system attempts to book a reservation and update the flight details without displaying them to the user first. John does not get the chance to review or confirm these changes before they are applied. It proceeds without obtaining an affirmative 'yes' from John."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = False

        user = User(user_id="john_456", name=Name(first_name="John", last_name="Smith"), address=Address(address1="456 Elm St", address2=None, city="Los Angeles", country="USA", state="CA", zip="90001"), email="john@example.com", dob="1985-05-05", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "john_456" else None

        flights = [FlightInfo(flight_number="FL456", date="2024-06-01")]
        passengers = [Passenger(first_name="John", last_name="Smith", dob="1985-05-05")]
        payment_methods = [Payment(payment_id="pay_002", amount=300)]

        with pytest.raises(PolicyViolationException):
            guard_user_confirmation_before_database_update(history, api, "john_456", "LAX", "JFK", "one_way", "business", flights, passengers, payment_methods, 3, 2, "no")
