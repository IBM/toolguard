from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_baggages.guard_explicit_confirmation_for_baggage_update import guard_explicit_confirmation_for_baggage_update
from airline.i_airline import *
from datetime import datetime, timedelta

class TestGuardExplicitConfirmationForBaggageUpdate:

    def test_compliance_example_user_confirms_yes(self):
        """
        Policy: "Before invoking the 'update_reservation_baggages' tool to update baggage information in a reservation, ensure you list all changes and receive explicit user confirmation (yes) to proceed."
        Example: "A user asks to update reservation 'ZFA04Y' baggages. The system lists changes: increasing total baggages from 2 to 3, nonfree from 0 to 2, using payment method 'certificate_7815826'. User explicitly confirms 'yes' and the operation proceeds."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = True  # Mock that user confirms 'yes'

        # Mock the API tool function return values
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[],
            payment_history=[],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        guard_explicit_confirmation_for_baggage_update(
            history=history,
            api=api,
            reservation_id="ZFA04Y",
            total_baggages=3,
            nonfree_baggages=2,
            payment_id="certificate_7815826"
        )

    def test_violation_example_no_explicit_confirmation(self):
        """
        Policy: "Before invoking the 'update_reservation_baggages' tool to update baggage information in a reservation, ensure you list all changes and receive explicit user confirmation (yes) to proceed."
        Example: "A user provides a reservation ID 'ZFA04Y' to update baggage details without explicitly confirming the changes. The system proceeds to update the total baggages to 3 and nonfree baggages to 1 using the payment method 'credit_card_7815826' without asking for explicit confirmation."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = False  # Mock that user does not confirm 'yes'

        # Mock the API tool function return values
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[],
            payment_history=[],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test and expect PolicyViolationException
        with pytest.raises(PolicyViolationException):
            guard_explicit_confirmation_for_baggage_update(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                total_baggages=3,
                nonfree_baggages=1,
                payment_id="credit_card_7815826"
            )
