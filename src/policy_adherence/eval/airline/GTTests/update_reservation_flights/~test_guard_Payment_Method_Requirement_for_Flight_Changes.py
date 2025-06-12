import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.update_reservation_flights.guard_update_reservation_flights import guard_update_reservation_flights
from my_app.common import *
from my_app.domain import *


class TestGuardPaymentMethodRequirementForFlightChanges(unittest.TestCase):
    
    @patch('my_app.domain.FlightBookingApi.get_user_details')
    def test_user_updates_flight_with_valid_credit_card(self, mock_get_user_details):
        """
        Test case for compliance: A user updates their flight details providing a valid payment ID for a credit card stored in their profile, like 'credit_card_7815826'.
        """
        # Mocking the API response
        user_details = GetUserDetailsResponse(payment_methods={
            'credit_card_7815826': PaymentMethods(source='credit_card', brand='Visa', last_four='1234', amount=100)
        })
        mock_get_user_details.return_value = user_details

        # Creating function call arguments
        args = UpdateReservationFlightsRequest(
            reservation_id='ZFA04Y',
            cabin='economy',
            flights=[Flight2(flight_number='HAT001', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )

        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = user_details

        # Invoke function under test
        guard_update_reservation_flights(args, history, api)

    @patch('my_app.domain.FlightBookingApi.get_user_details')
    def test_user_attempts_update_with_unlinked_payment_id(self, mock_get_user_details):
        """
        Test case for violation: A user attempts to update flight details but provides a payment ID that is not linked to any payment method saved in their profile, such as 'unlinked_card_12345', violating the requirement for a valid payment method.
        """
        # Mocking the API response
        user_details = GetUserDetailsResponse(payment_methods={
            'credit_card_7815826': PaymentMethods(source='credit_card', brand='Visa', last_four='1234', amount=100)
        })
        mock_get_user_details.return_value = user_details

        # Creating function call arguments
        args = UpdateReservationFlightsRequest(
            reservation_id='ZFA04Y',
            cabin='economy',
            flights=[Flight2(flight_number='HAT001', date='2024-05-01')],
            payment_id='unlinked_card_12345'
        )

        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = user_details

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_update_reservation_flights(args, history, api)

        self.assertEqual(str(context.exception), "Payment method 'unlinked_card_12345' is not linked to any saved payment method.")

    # Additional tests for other compliance and violation examples can be added here


if __name__ == '__main__':
    unittest.main()
