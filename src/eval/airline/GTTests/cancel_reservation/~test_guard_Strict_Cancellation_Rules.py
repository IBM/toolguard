import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.cancel_reservation.guard_cancel_reservation import guard_cancel_reservation
from my_app.common import *
from my_app.domain import *


class TestStrictCancellationRules(unittest.TestCase):
    
    # Compliance test: Business class reservation cancellation without membership check
    def test_business_class_cancellation_without_membership_check(self):
        """
        The agent cancels a business class reservation without checking user membership status and confirms that no flight segments are used.
        """
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')
        history = MagicMock()
        history.ask_bool.return_value = True  # Mock that all segments are unused
        api = MagicMock()
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(cabin='business')

        # Invoke function under test
        guard_cancel_reservation(args, history, api)

    # Compliance test: Economy flight cancellation due to airline cancellation
    def test_economy_flight_cancellation_due_to_airline(self):
        """
        An agent cancels an economy flight reservation by confirming the airline has canceled the flight.
        """
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')
        history = MagicMock()
        history.ask_bool.return_value = True  # Mock that airline canceled the flight
        api = MagicMock()
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(cabin='economy')

        # Invoke function under test
        guard_cancel_reservation(args, history, api)

    # Violation test: Basic economy cancellation without travel insurance
    def test_basic_economy_cancellation_without_insurance(self):
        """
        An agent attempts to cancel a basic economy flight reservation without travel insurance purchased, and the flight is not canceled by the airline.
        """
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')
        history = MagicMock()
        history.ask_bool.return_value = False  # Mock that airline did not cancel the flight
        api = MagicMock()
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(cabin='basic_economy', insurance='no')

        # Expecting PolicyViolationException
        with self.assertRaises(PolicyViolationException):
            guard_cancel_reservation(args, history, api)

    # Violation test: Economy class cancellation after 24 hours without insurance
    def test_economy_class_cancellation_after_24_hours_without_insurance(self):
        """
        The agent tries to cancel an economy class flight after 24 hours of booking without verifying travel insurance purchase, and the flight is not canceled by the airline.
        """
        args = CancelReservationRequest.model_construct(reservation_id='ZFA04Y')
        history = MagicMock()
        history.ask_bool.return_value = False  # Mock that airline did not cancel the flight
        api = MagicMock()
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(cabin='economy', insurance='no')

        # Expecting PolicyViolationException
        with self.assertRaises(PolicyViolationException):
            guard_cancel_reservation(args, history, api)


if __name__ == '__main__':
    unittest.main()
