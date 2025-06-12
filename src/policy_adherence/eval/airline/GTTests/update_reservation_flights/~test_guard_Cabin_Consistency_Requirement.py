import unittest
from unittest.mock import MagicMock, patch

# Importing the function under test and necessary modules
from my_app.update_reservation_flights.guard_update_reservation_flights import guard_update_reservation_flights
from my_app.common import *
from my_app.domain import *


class TestGuardCabinConsistencyRequirement(unittest.TestCase):
    
    @patch('my_app.update_reservation_flights.guard_update_reservation_flights.FlightBookingApi')
    def test_compliance_all_segments_business(self, MockApi):
        """
        Test compliance: Updating a reservation for multiple flight segments where all are consistently set to 'business' cabin.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Constructing the request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='ABC123',
            cabin='business',
            flights=[
                Flight2.model_construct(flight_number='FL001', date='2024-05-01'),
                Flight2.model_construct(flight_number='FL002', date='2024-05-02')
            ],
            payment_id='credit_card_123456'
        )

        # Mocking dependent tool
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id='ABC123',
            cabin='business',
            flights=[
                Flight3.model_construct(flight_number='FL001'),
                Flight3.model_construct(flight_number='FL002')
            ]
        )

        # Invoke the function under test
        guard_update_reservation_flights(args, history, api)

    @patch('my_app.update_reservation_flights.guard_update_reservation_flights.FlightBookingApi')
    def test_compliance_all_segments_first(self, MockApi):
        """
        Test compliance: Modifying a reservation to change all flights uniformly to 'first' cabin.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Constructing the request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='DEF456',
            cabin='first',
            flights=[
                Flight2.model_construct(flight_number='FL003', date='2024-06-01'),
                Flight2.model_construct(flight_number='FL004', date='2024-06-02')
            ],
            payment_id='credit_card_654321'
        )

        # Mocking dependent tool
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id='DEF456',
            cabin='first',
            flights=[
                Flight3.model_construct(flight_number='FL003'),
                Flight3.model_construct(flight_number='FL004')
            ]
        )

        # Invoke the function under test
        guard_update_reservation_flights(args, history, api)

    @patch('my_app.update_reservation_flights.guard_update_reservation_flights.FlightBookingApi')
    def test_compliance_all_segments_economy(self, MockApi):
        """
        Test compliance: Ensuring that all flight segments in a reservation remain in 'economy' cabin.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Constructing the request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='GHI789',
            cabin='economy',
            flights=[
                Flight2.model_construct(flight_number='FL005', date='2024-07-01'),
                Flight2.model_construct(flight_number='FL006', date='2024-07-02')
            ],
            payment_id='credit_card_789012'
        )

        # Mocking dependent tool
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id='GHI789',
            cabin='economy',
            flights=[
                Flight3.model_construct(flight_number='FL005'),
                Flight3.model_construct(flight_number='FL006')
            ]
        )

        # Invoke the function under test
        guard_update_reservation_flights(args, history, api)

    @patch('my_app.update_reservation_flights.guard_update_reservation_flights.FlightBookingApi')
    def test_violation_different_cabin_classes(self, MockApi):
        """
        Test violation: Attempting to update a reservation with multiple flights where different flight segments are assigned different cabin classes.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Constructing the request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='JKL012',
            cabin='economy',
            flights=[
                Flight2.model_construct(flight_number='FL007', date='2024-08-01'),
                Flight2.model_construct(flight_number='FL008', date='2024-08-02')
            ],
            payment_id='credit_card_345678'
        )

        # Mocking dependent tool
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            reservation_id='JKL012',
            cabin='business',  # Different cabin class to simulate violation
            flights=[
                Flight3.model_construct(flight_number='FL007'),
                Flight3.model_construct(flight_number='FL008')
            ]
        )

        # Invoke the function under test and expect an exception
        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException for inconsistent cabin classes"):
            guard_update_reservation_flights(args, history, api)


if __name__ == '__main__':
    unittest.main()
