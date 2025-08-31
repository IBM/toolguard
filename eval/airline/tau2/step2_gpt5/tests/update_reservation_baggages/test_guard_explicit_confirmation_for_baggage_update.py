from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_baggages.guard_explicit_confirmation_for_baggage_update import guard_explicit_confirmation_for_baggage_update
from airline.i_airline import *
from airline.airline_types import *

class TestGuardExplicitConfirmationForBaggageUpdate:

    def test_increase_baggage_with_confirmation(self):
        """ 
        Policy: Before invoking the 'update_reservation_baggages' tool to update baggage information in a reservation, ensure you list all changes and receive explicit user confirmation (yes) to proceed.
        Example: A user asks to update reservation 'ZFA04Y' baggages. The system lists changes: increasing total baggages from 2 to 3, nonfree from 0 to 2, using payment method 'certificate_7815826'. User explicitly confirms 'yes' and the operation proceeds.
        """
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
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None

        # Should not raise
        guard_explicit_confirmation_for_baggage_update(api, reservation_id="ZFA04Y", total_baggages=3, nonfree_baggages=2, payment_id="certificate_7815826")

    def test_update_without_explicit_confirmation(self):
        """ 
        Policy: Before invoking the 'update_reservation_baggages' tool to update baggage information in a reservation, ensure you list all changes and receive explicit user confirmation (yes) to proceed.
        Example: A user provides a reservation ID 'ZFA04Y' to update baggage details without explicitly confirming the changes. The system proceeds to update the total baggages to 3 and nonfree baggages to 1 using the payment method 'credit_card_7815826' without asking for explicit confirmation.
        """
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
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_explicit_confirmation_for_baggage_update(api, reservation_id="ZFA04Y", total_baggages=3, nonfree_baggages=1, payment_id="credit_card_7815826")

    def test_reduce_baggage_with_confirmation(self):
        """ 
        Policy: Before invoking the 'update_reservation_baggages' tool to update baggage information in a reservation, ensure you list all changes and receive explicit user confirmation (yes) to proceed.
        Example: Before updating the reservation 'XJ43MS', the agent presents a summary of requested changes: altering total baggages to 5 and nonfree baggages to 3. The user confirms with a 'yes', allowing the update to take place using 'gift_card_987654'.
        """
        reservation = Reservation(
            reservation_id="XJ43MS",
            user_id="user456",
            origin="LAX",
            destination="ORD",
            flight_type="one_way",
            cabin="business",
            flights=[],
            passengers=[],
            payment_history=[],
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=6,
            nonfree_baggages=4,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "XJ43MS" else None

        # Should not raise
        guard_explicit_confirmation_for_baggage_update(api, reservation_id="XJ43MS", total_baggages=5, nonfree_baggages=3, payment_id="gift_card_987654")

    def test_update_without_listing_changes(self):
        """ 
        Policy: Before invoking the 'update_reservation_baggages' tool to update baggage information in a reservation, ensure you list all changes and receive explicit user confirmation (yes) to proceed.
        Example: An agent wishes to update the baggage count by reducing total baggages from 5 to 3 using reservation ID 'T125HG' and payment method 'gift_card_123456', but does not list the changes beforehand or seek affirmation from the user.
        """
        reservation = Reservation(
            reservation_id="T125HG",
            user_id="user789",
            origin="SEA",
            destination="MIA",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[],
            payment_history=[],
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=5,
            nonfree_baggages=2,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "T125HG" else None

        with pytest.raises(PolicyViolationException):
            guard_explicit_confirmation_for_baggage_update(api, reservation_id="T125HG", total_baggages=3, nonfree_baggages=2, payment_id="gift_card_123456")