import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules from the application
from my_app.book_reservation.check_Travel_Insurance_Option import check_Travel_Insurance_Option
from my_app.common import *
from my_app.domain import *

class TestCheckTravelInsuranceOption(unittest.TestCase):
    
    @patch('my_app.book_reservation.check_Travel_Insurance_Option.FlightBookingApi')
    def test_ask_user_for_insurance_compliance(self, MockApi):
        """
        The agent completes the reservation by first asking the user if they would like travel insurance for $30 per passenger, resulting in 'insurance':'yes' when the user agrees.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True  # Simulate user agreeing to insurance

        # Constructing the request
        args = BookReservationRequest(
            user_id='user_123',
            origin='SFO',
            destination='JFK',
            flight_type='round_trip',
            cabin='economy',
            flights=[Flight(flight_number='FL123', date='2024-05-01')],
            passengers=[Passenger(first_name='John', last_name='Doe', dob='1990-01-01')],
            payment_methods=[PaymentMethod(payment_id='credit_card_123', amount=300.0)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance='yes'
        )

        # Call the function under test
        check_Travel_Insurance_Option(args, history, api)

    @patch('my_app.book_reservation.check_Travel_Insurance_Option.FlightBookingApi')
    def test_no_insurance_inquiry_violation(self, MockApi):
        """
        A reservation is booked without asking the user if they want to purchase travel insurance, thus the 'insurance' parameter is set to 'no' without confirming the user's decision, violating the policy requirements.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # Simulate no inquiry made

        # Constructing the request
        args = BookReservationRequest(
            user_id='user_123',
            origin='SFO',
            destination='JFK',
            flight_type='round_trip',
            cabin='economy',
            flights=[Flight(flight_number='FL123', date='2024-05-01')],
            passengers=[Passenger(first_name='John', last_name='Doe', dob='1990-01-01')],
            payment_methods=[PaymentMethod(payment_id='credit_card_123', amount=300.0)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance='no'
        )

        # Expecting a PolicyViolationException
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when insurance inquiry is skipped."):
            check_Travel_Insurance_Option(args, history, api)

    @patch('my_app.book_reservation.check_Travel_Insurance_Option.FlightBookingApi')
    def test_direct_charge_without_insurance_offer_violation(self, MockApi):
        """
        The agent skips offering travel insurance and directly charges the user's payment method and issues a receipt without ever addressing insurance. As a result, the insurance option is omitted from the final reservation details.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # Simulate no inquiry made

        # Constructing the request
        args = BookReservationRequest(
            user_id='user_123',
            origin='SFO',
            destination='JFK',
            flight_type='round_trip',
            cabin='economy',
            flights=[Flight(flight_number='FL123', date='2024-05-01')],
            passengers=[Passenger(first_name='John', last_name='Doe', dob='1990-01-01')],
            payment_methods=[PaymentMethod(payment_id='credit_card_123', amount=300.0)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance='no'
        )

        # Expecting a PolicyViolationException
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when insurance offer is skipped and direct charge is made."):
            check_Travel_Insurance_Option(args, history, api)

    @patch('my_app.book_reservation.check_Travel_Insurance_Option.FlightBookingApi')
    def test_assumed_no_insurance_without_check_violation(self, MockApi):
        """
        While gathering passenger information, the agent incorrectly assumes that the user does not want insurance based on lack of explicit inquiry, and fills 'insurance':'no' by default without a deliberate check.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False  # Simulate no inquiry made

        # Constructing the request
        args = BookReservationRequest(
            user_id='user_123',
            origin='SFO',
            destination='JFK',
            flight_type='round_trip',
            cabin='economy',
            flights=[Flight(flight_number='FL123', date='2024-05-01')],
            passengers=[Passenger(first_name='John', last_name='Doe', dob='1990-01-01')],
            payment_methods=[PaymentMethod(payment_id='credit_card_123', amount=300.0)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance='no'
        )

        # Expecting a PolicyViolationException
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when insurance is assumed 'no' without explicit check."):
            check_Travel_Insurance_Option(args, history, api)

if __name__ == '__main__':
    unittest.main()
