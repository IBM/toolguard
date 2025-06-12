import unittest
from unittest.mock import MagicMock, patch

# Importing the function under test and necessary modules
from my_app.update_reservation_baggages.guard_update_reservation_baggages import guard_update_reservation_baggages
from my_app.common import *
from my_app.domain import *


class TestGuardExplicitUserConfirmationForBaggageUpdate(unittest.TestCase):
    
    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_compliance_user_confirms_baggage_update(self, MockApi):
        """
        The system presents the user with the baggage update details, asking for explicit confirmation. 
        The update proceeds only after the user responds with 'yes', adhering to the policy requirements.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True  # Mock user confirmation as 'yes'

        # Constructing the request
        args = UpdateReservationBaggagesRequest.model_construct(
            reservation_id='ZFA04Y',
            total_baggages=3,
            nonfree_baggages=1,
            payment_id='credit_card_7815826'
        )

        # Call the function under test
        guard_update_reservation_baggages(args, history, api)

    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_violation_no_user_confirmation(self, MockApi):
        """
        The system attempts to update a reservation's baggage details with total baggages as 5, 
        non-free baggages as 2, and uses payment ID 'credit_card_7815826' without confirming these details with the user.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # Mock user did not confirm

        # Constructing the request
        args = UpdateReservationBaggagesRequest.model_construct(
            reservation_id='ZFA04Y',
            total_baggages=5,
            nonfree_baggages=2,
            payment_id='credit_card_7815826'
        )

        # Call the function under test and expect a PolicyViolationException
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when user confirmation is not obtained."):
            guard_update_reservation_baggages(args, history, api)

    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_violation_backend_process_without_confirmation(self, MockApi):
        """
        A backend process updates the baggage numbers without any explicit confirmation from the user, 
        in breach of the policy requiring action confirmation.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # Mock user did not confirm

        # Constructing the request
        args = UpdateReservationBaggagesRequest.model_construct(
            reservation_id='ZFA04Y',
            total_baggages=4,
            nonfree_baggages=2,
            payment_id='gift_card_7815826'
        )

        # Call the function under test and expect a PolicyViolationException
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when backend process updates without user confirmation."):
            guard_update_reservation_baggages(args, history, api)


if __name__ == '__main__':
    unittest.main()
