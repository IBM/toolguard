import unittest
from unittest.mock import MagicMock, patch

from my_app.cancel_reservation.guard_cancel_reservation import guard_cancel_reservation
from my_app.common import *
from my_app.domain import *


class TestGuardUserIDAndReservationIDRequirementForCancellation(unittest.TestCase):
    
    @patch('my_app.domain.FlightBookingApi')
    def test_compliance_with_change_of_plan(self, MockApi):
        """
        Canceling a reservation with reservation ID '4WQ150', user ID 'chen_jackson_3290', and reason 'change of plan', complying with all policy requirements.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Construct the request
        args = CancelReservationRequest.model_construct(reservation_id='4WQ150')

        # Mock the dependent tools
        user_details = GetUserDetailsResponse.model_construct(user_id='chen_jackson_3290')
        reservation_details = GetReservationDetailsResponse.model_construct(reservation_id='4WQ150')
        api.get_user_details.return_value = user_details
        api.get_reservation_details.return_value = reservation_details

        # Call the function under test
        guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_missing_user_id(self, MockApi):
        """
        Attempting to cancel a reservation with reservation ID '4WQ150' without providing the user ID, violating the policy requirement for both user and reservation IDs.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Construct the request
        args = CancelReservationRequest.model_construct(reservation_id='4WQ150')

        # Mock the dependent tools
        reservation_details = GetReservationDetailsResponse.model_construct(reservation_id='4WQ150')
        api.get_reservation_details.return_value = reservation_details

        # Call the function under test and expect an exception
        with self.assertRaises(PolicyViolationException):
            guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_missing_reason(self, MockApi):
        """
        Cancelling a reservation with reservation ID 'ZFA04Y' without mentioning any reason for the cancellation, which breaches the policy that mandates a valid reason.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # Simulate no valid reason provided

        # Construct the request
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')

        # Mock the dependent tools
        user_details = GetUserDetailsResponse.model_construct(user_id='robert_anderson_4523')
        reservation_details = GetReservationDetailsResponse.model_construct(reservation_id='ZFA04Y')
        api.get_user_details.return_value = user_details
        api.get_reservation_details.return_value = reservation_details

        # Call the function under test and expect an exception
        with self.assertRaises(PolicyViolationException):
            guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_invalid_reason(self, MockApi):
        """
        The cancellation reason 'personal reasons' for reservation ID 'NO6JO3' is not listed as valid according to policy, hence violating the specified valid reasons requirement.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # Simulate invalid reason provided

        # Construct the request
        args = CancelReservationRequest.model_construct(reservation_id='NO6JO3')

        # Mock the dependent tools
        user_details = GetUserDetailsResponse.model_construct(user_id='emily_taylor_9987')
        reservation_details = GetReservationDetailsResponse.model_construct(reservation_id='NO6JO3')
        api.get_user_details.return_value = user_details
        api.get_reservation_details.return_value = reservation_details

        # Call the function under test and expect an exception
        with self.assertRaises(PolicyViolationException):
            guard_cancel_reservation(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_missing_valid_reason(self, MockApi):
        """
        Attempting to cancel a reservation for user ID 'lisa_miller_1820' with reservation ID 'X104L6', omitting a valid reason for cancellation, contravening the policy's requirement.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # Simulate no valid reason provided

        # Construct the request
        args = CancelReservationRequest.model_construct(reservation_id='X104L6')

        # Mock the dependent tools
        user_details = GetUserDetailsResponse.model_construct(user_id='lisa_miller_1820')
        reservation_details = GetReservationDetailsResponse.model_construct(reservation_id='X104L6')
        api.get_user_details.return_value = user_details
        api.get_reservation_details.return_value = reservation_details

        # Call the function under test and expect an exception
        with self.assertRaises(PolicyViolationException):
            guard_cancel_reservation(args, history, api)


if __name__ == '__main__':
    unittest.main()
