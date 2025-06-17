import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.book_reservation.check_User_Confirmation_Required_for_Action import check_User_Confirmation_Required_for_Action
from my_app.common import *
from my_app.domain import *

class TestUserConfirmationRequiredForAction(unittest.TestCase):
    
    @patch('my_app.domain.FlightBookingApi')
    def test_user_confirmation_compliance_booking(self, MockApi):
        """
        Test compliance: The user requests a reservation from SFO to JFK. Before executing the booking, the system lists all details, including flight number, passenger names, and payment amount, and receives a 'yes' confirmation from the user before finalizing the booking.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Creating request object
        args = BookReservationRequest(
            user_id='sara_doe_496',
            origin='SFO',
            destination='JFK',
            flight_type='one_way',
            cabin='economy',
            flights=[Flight(flight_number='HAT001', date='2024-05-01')],
            passengers=[Passenger(first_name='Noah', last_name='Brown', dob='1990-01-01')],
            payment_methods=[PaymentMethod(payment_id='credit_card_7815826', amount=500.0)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance='yes'
        )

        # Mocking dependent tools
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse()
        api.search_direct_flight.return_value = []
        api.search_onestop_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.get_reservation_details.return_value = GetReservationDetailsResponse()
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()

        # Invoke function under test
        check_User_Confirmation_Required_for_Action(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_user_confirmation_violation_booking(self, MockApi):
        """
        Test violation: The user initiates the booking process for a reservation from SFO to JFK, including all relevant details such as flight number, passenger names, and payment methods, but the booking is completed without obtaining the user's explicit confirmation ('yes').
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False

        # Creating request object
        args = BookReservationRequest(
            user_id='sara_doe_496',
            origin='SFO',
            destination='JFK',
            flight_type='one_way',
            cabin='economy',
            flights=[Flight(flight_number='HAT001', date='2024-05-01')],
            passengers=[Passenger(first_name='Noah', last_name='Brown', dob='1990-01-01')],
            payment_methods=[PaymentMethod(payment_id='credit_card_7815826', amount=500.0)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance='yes'
        )

        # Mocking dependent tools
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse()
        api.search_direct_flight.return_value = []
        api.search_onestop_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.get_reservation_details.return_value = GetReservationDetailsResponse()
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException):
            check_User_Confirmation_Required_for_Action(args, history, api)

# Additional tests for other compliance and violation examples can be added following the same pattern.

if __name__ == '__main__':
    unittest.main()
