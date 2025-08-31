from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_explicit_user_confirmation_required import guard_explicit_user_confirmation_required
from airline.airline_types import *
from airline.i_airline import *

class TestGuardExplicitUserConfirmationRequired:

    def test_compliance_with_explicit_yes_before_update(self):
        """ 
        Policy: "Before using ToolX for reservation updates including flights, baggage, cabin class, or passenger information, ensure you present all action details to the user in a clear manner and receive their explicit confirmation (yes) to proceed."
        Example: "The agent presents the updated flight itinerary, cabin class changes, and passenger adjustments in detail and waits for the user to reply 'yes' before proceeding, ensuring compliance with the required user confirmation."
        """
        api = MagicMock(spec=I_Airline)
        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]
        # Should not raise exception for compliance
        guard_explicit_user_confirmation_required(api, reservation_id="ZFA04Y", cabin="business", flights=flights, payment_id="credit_card_7815826")

    def test_violation_no_confirmation_before_update(self):
        """ 
        Policy: "Before using ToolX for reservation updates including flights, baggage, cabin class, or passenger information, ensure you present all action details to the user in a clear manner and receive their explicit confirmation (yes) to proceed."
        Example: "An agent updates the flight details of a reservation without asking the user for confirmation, proceeding with changes based on assumed preferences, which violates the requirement for explicit user consent."
        """
        api = MagicMock(spec=I_Airline)
        flights = [FlightInfo(flight_number="HAT002", date="2024-06-01")]
        with pytest.raises(PolicyViolationException):
            guard_explicit_user_confirmation_required(api, reservation_id="ZFA04Y", cabin="economy", flights=flights, payment_id="gift_card_7815826")

    def test_violation_implicit_consent_not_yes(self):
        """ 
        Policy: "Before using ToolX for reservation updates including flights, baggage, cabin class, or passenger information, ensure you present all action details to the user in a clear manner and receive their explicit confirmation (yes) to proceed."
        Example: "A reservation update is initiated after receiving implicit consent from phrases like 'okay' or 'sounds good', rather than a clear 'yes', which does not meet the policy's explicit confirmation standard."
        """
        api = MagicMock(spec=I_Airline)
        flights = [FlightInfo(flight_number="HAT003", date="2024-07-01")]
        with pytest.raises(PolicyViolationException):
            guard_explicit_user_confirmation_required(api, reservation_id="ZFA04Y", cabin="basic_economy", flights=flights, payment_id="certificate_7815826")