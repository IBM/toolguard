import unittest
from unittest.mock import MagicMock, patch

from my_app.update_reservation_baggages.guard_update_reservation_baggages import guard_update_reservation_baggages
from my_app.common import *
from my_app.domain import *


class TestStoredPaymentMethodsValidation(unittest.TestCase):
    
    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_compliance_with_pre_registered_credit_card(self, MockApi):
        """
        Test compliance: Updating reservation baggage using a pre-registered 'credit_card_1234567', complies with the policy requiring payment methods to be stored in the user's profile.
        """
        # Mock the API and history
        api = MockApi()
        user_details = GetUserDetailsResponse(
            payment_methods={
                'credit_card_1234567': PaymentMethods(source='credit_card', brand='Visa', last_four='1234', amount=1000)
            }
        )
        api.get_user_details.return_value = user_details

        history = MagicMock()
        history.ask_bool.return_value = True

        # Construct the request
        args = UpdateReservationBaggagesRequest(
            reservation_id='res_001',
            total_baggages=2,
            nonfree_baggages=1,
            payment_id='credit_card_1234567'
        )

        # Call the function under test
        guard_update_reservation_baggages(args, history, api)

    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_violation_with_non_registered_payment_id(self, MockApi):
        """
        Test violation: Attempting to update baggage information using a non-registered payment ID 'unknown_certificate_0016432' violates the policy requiring payment methods to be pre-registered in the user's profile.
        """
        # Mock the API and history
        api = MockApi()
        user_details = GetUserDetailsResponse(
            payment_methods={
                'credit_card_1234567': PaymentMethods(source='credit_card', brand='Visa', last_four='1234', amount=1000)
            }
        )
        api.get_user_details.return_value = user_details

        history = MagicMock()
        history.ask_bool.return_value = True

        # Construct the request
        args = UpdateReservationBaggagesRequest(
            reservation_id='res_002',
            total_baggages=2,
            nonfree_baggages=1,
            payment_id='unknown_certificate_0016432'
        )

        # Call the function under test and expect an exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_update_reservation_baggages(args, history, api)

        self.assertEqual(str(context.exception), "Payment method 'unknown_certificate_0016432' is not registered in the user's profile.")

    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_compliance_with_multiple_gift_cards(self, MockApi):
        """
        Test compliance: Applying 'gift_card_654321', 'gift_card_654322', and 'gift_card_654323', all found in the user's profile, complies with the maximum of three gift cards rule.
        """
        # Mock the API and history
        api = MockApi()
        user_details = GetUserDetailsResponse(
            payment_methods={
                'gift_card_654321': PaymentMethods(source='gift_card', brand='Amazon', last_four='4321', amount=50),
                'gift_card_654322': PaymentMethods(source='gift_card', brand='Amazon', last_four='4322', amount=50),
                'gift_card_654323': PaymentMethods(source='gift_card', brand='Amazon', last_four='4323', amount=50)
            }
        )
        api.get_user_details.return_value = user_details

        history = MagicMock()
        history.ask_bool.return_value = True

        # Construct the request
        args = UpdateReservationBaggagesRequest(
            reservation_id='res_003',
            total_baggages=2,
            nonfree_baggages=1,
            payment_id='gift_card_654321'
        )

        # Call the function under test
        guard_update_reservation_baggages(args, history, api)

    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_violation_with_excessive_gift_cards(self, MockApi):
        """
        Test violation: Submitting a request with more than three gift card IDs, e.g., 'gift_card_1', 'gift_card_2', 'gift_card_3', 'gift_card_4', contravenes the policy limit.
        """
        # Mock the API and history
        api = MockApi()
        user_details = GetUserDetailsResponse(
            payment_methods={
                'gift_card_1': PaymentMethods(source='gift_card', brand='Amazon', last_four='0001', amount=50),
                'gift_card_2': PaymentMethods(source='gift_card', brand='Amazon', last_four='0002', amount=50),
                'gift_card_3': PaymentMethods(source='gift_card', brand='Amazon', last_four='0003', amount=50),
                'gift_card_4': PaymentMethods(source='gift_card', brand='Amazon', last_four='0004', amount=50)
            }
        )
        api.get_user_details.return_value = user_details

        history = MagicMock()
        history.ask_bool.return_value = True

        # Construct the request
        args = UpdateReservationBaggagesRequest(
            reservation_id='res_004',
            total_baggages=2,
            nonfree_baggages=1,
            payment_id='gift_card_1'
        )

        # Call the function under test and expect an exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_update_reservation_baggages(args, history, api)

        self.assertEqual(str(context.exception), "Exceeds the maximum of three gift cards allowed.")


if __name__ == '__main__':
    unittest.main()
