import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.cancel_reservation.guard_cancel_reservation import guard_cancel_reservation
from my_app.common import *
from my_app.domain import *


class TestGuardCancellationReasonRequirement(unittest.TestCase):
    
    @patch('my_app.domain.FlightBookingApi.get_reservation_details')
    def test_compliance_airline_cancelled_flight(self, mock_get_reservation_details):
        """
        Test compliance: The agent gathers the reservation ID and cancellation reason 'airline cancelled flight', then cancels the reservation ensuring all conditions are met according to policy.
        """
        # Mocking the API response
        mock_get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id='ZFA04Y',
            cabin='economy',
            insurance='yes'
        )

        # Creating function call arguments
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')
        history = MagicMock()
        history.ask_bool.return_value = True  # Mocking that the cancellation reason is 'airline cancelled flight'

        api = MagicMock()
        api.get_reservation_details.return_value = mock_get_reservation_details.return_value

        # Invoke function under test
        guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi.get_reservation_details')
    def test_violation_no_reservation_id_or_reason(self, mock_get_reservation_details):
        """
        Test violation: The agent attempts to cancel a reservation without providing a reservation ID or reason for cancellation, violating the policy requirement to gather necessary details.
        """
        # Mocking the API response
        mock_get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id=None,
            cabin='economy',
            insurance='no'
        )

        # Creating function call arguments
        args = CancelReservationRequest.model_construct(reservation_id='')
        history = MagicMock()
        history.ask_bool.return_value = False  # Mocking that no cancellation reason is provided

        api = MagicMock()
        api.get_reservation_details.return_value = mock_get_reservation_details.return_value

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_cancel_reservation(args, history, api)

        self.assertEqual(str(context.exception), "Policy violation: Missing reservation ID or cancellation reason.")

    @patch('my_app.domain.FlightBookingApi.get_reservation_details')
    def test_violation_after_24_hours_without_conditions(self, mock_get_reservation_details):
        """
        Test violation: The agent tries to cancel a reservation after the 24-hour period without checking if it's due to airline cancellation or a business class ticket, which is against policy stipulations.
        """
        # Mocking the API response
        mock_get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id='ZFA04Y',
            cabin='economy',
            insurance='no'
        )

        # Creating function call arguments
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')
        history = MagicMock()
        history.ask_bool.return_value = False  # Mocking that the cancellation reason is not valid

        api = MagicMock()
        api.get_reservation_details.return_value = mock_get_reservation_details.return_value

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_cancel_reservation(args, history, api)

        self.assertEqual(str(context.exception), "Policy violation: Cancellation conditions not met.")

    @patch('my_app.domain.FlightBookingApi.get_reservation_details')
    def test_compliance_within_24_hours_change_of_plans(self, mock_get_reservation_details):
        """
        Test compliance: Reservation ID 'ZFA04Y' and reason 'change of plans' are presented within 24 hours of booking, enabling the agent to proceed with cancellation following policy criteria.
        """
        # Mocking the API response
        mock_get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id='ZFA04Y',
            cabin='economy',
            insurance='yes'
        )

        # Creating function call arguments
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')
        history = MagicMock()
        history.ask_bool.return_value = True  # Mocking that the cancellation reason is 'change of plans'

        api = MagicMock()
        api.get_reservation_details.return_value = mock_get_reservation_details.return_value

        # Invoke function under test
        guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi.get_reservation_details')
    def test_violation_economy_no_insurance(self, mock_get_reservation_details):
        """
        Test violation: The agent tries to cancel an economy reservation without validating that travel insurance was bought or the conditions allowing cancellation are met, neglecting policy guidelines.
        """
        # Mocking the API response
        mock_get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id='ZFA04Y',
            cabin='economy',
            insurance='no'
        )

        # Creating function call arguments
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')
        history = MagicMock()
        history.ask_bool.return_value = False  # Mocking that the cancellation reason is not valid

        api = MagicMock()
        api.get_reservation_details.return_value = mock_get_reservation_details.return_value

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_cancel_reservation(args, history, api)

        self.assertEqual(str(context.exception), "Policy violation: Insurance not validated for economy class.")


if __name__ == '__main__':
    unittest.main()
