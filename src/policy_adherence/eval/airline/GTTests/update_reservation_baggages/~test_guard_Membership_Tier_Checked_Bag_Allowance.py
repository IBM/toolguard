import unittest
from unittest.mock import MagicMock, patch

from my_app.update_reservation_baggages.guard_update_reservation_baggages import guard_update_reservation_baggages
from my_app.common import *
from my_app.domain import *


class TestGuardMembershipTierCheckedBagAllowance(unittest.TestCase):
    
    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_regular_member_business_class_with_extra_bag(self, MockApi):
        """
        Regular member updates a reservation in business class with a total of 3 baggage items, including 1 non-free bag and uses a certificate payment method stored in profile.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the return value of get_user_details
        user_details = GetUserDetailsResponse.model_construct(
            membership='regular',
            payment_methods={'certificate': PaymentMethods(source='certificate', brand='Visa', last_four='1234', amount=100)}
        )
        api.get_user_details.return_value = user_details

        # Create request
        args = UpdateReservationBaggagesRequest.model_construct(
            reservation_id='ABC123',
            total_baggages=3,
            nonfree_baggages=1,
            payment_id='certificate'
        )

        # Call the function under test
        guard_update_reservation_baggages(args, history, api)

    @patch('my_app.update_reservation_baggages.guard_update_reservation_baggages.FlightBookingApi')
    def test_regular_member_basic_economy_with_one_free_bag(self, MockApi):
        """
        Regular member attempts to update reservation in basic economy with 1 free baggage, violating the allowance of 0 free bags per passenger.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the return value of get_user_details
        user_details = GetUserDetailsResponse.model_construct(
            membership='regular',
            payment_methods={'credit_card_1234567': PaymentMethods(source='credit_card', brand='Visa', last_four='1234', amount=100)}
        )
        api.get_user_details.return_value = user_details

        # Create request
        args = UpdateReservationBaggagesRequest.model_construct(
            reservation_id='DEF456',
            total_baggages=1,
            nonfree_baggages=0,
            payment_id='credit_card_1234567'
        )

        # Call the function under test and expect a PolicyViolationException
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_baggages(args, history, api)

    # Additional tests for other compliance and violation examples can be added here


if __name__ == '__main__':
    unittest.main()
