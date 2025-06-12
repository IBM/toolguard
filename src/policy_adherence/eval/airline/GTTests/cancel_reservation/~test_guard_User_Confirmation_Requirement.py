import unittest
from unittest.mock import MagicMock, patch

from my_app.cancel_reservation.guard_cancel_reservation import guard_cancel_reservation
from my_app.common import *
from my_app.domain import *


class TestGuardUserConfirmationRequirement(unittest.TestCase):
    
    @patch('my_app.domain.FlightBookingApi')
    def test_compliance_user_confirms_cancellation(self, MockApi):
        """
        An agent shows the user the details of reservation cancellation, and the user replies with 'yes' to confirm, complying with the explicit confirmation requirement.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True  # User confirms with 'yes'

        # Create a CancelReservationRequest
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')

        # Call the function under test
        guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_no_user_confirmation(self, MockApi):
        """
        A reservation cancellation is processed automatically without presenting the cancellation details to the user, violating the policy requiring explicit user confirmation.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # User does not confirm

        # Create a CancelReservationRequest
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')

        # Call the function under test and expect a PolicyViolationException
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when user confirmation is not obtained."):
            guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_compliance_system_sends_summary_and_receives_yes(self, MockApi):
        """
        The system sends an action details summary for the reservation cancellation to the user's app, and proceeds only after receiving 'yes' from the user.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True  # User confirms with 'yes'

        # Create a CancelReservationRequest
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')

        # Call the function under test
        guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_cancellation_without_confirmation(self, MockApi):
        """
        The system cancels a reservation after receiving a user's request, but without confirming the details with the user by securing a 'yes'.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # User does not confirm

        # Create a CancelReservationRequest
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')

        # Call the function under test and expect a PolicyViolationException
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when user confirmation is not obtained."):
            guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_compliance_confirmation_dialogue_on_portal(self, MockApi):
        """
        A confirmation dialogue is presented on the user's portal showing cancellation details, and only performs the cancellation once the user clicks 'Yes'.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True  # User confirms with 'yes'

        # Create a CancelReservationRequest
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')

        # Call the function under test
        guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_implicit_consent_without_confirmation(self, MockApi):
        """
        The reservation is canceled based on implicit consent inferred from user inactivity, without asking for explicit confirmation.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # User does not confirm

        # Create a CancelReservationRequest
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')

        # Call the function under test and expect a PolicyViolationException
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when user confirmation is not obtained."):
            guard_cancel_reservation(args, history, api)


if __name__ == '__main__':
    unittest.main()
