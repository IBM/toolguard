import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.update_reservation_flights.guard_update_reservation_flights import guard_update_reservation_flights
from my_app.common import *
from my_app.domain import *


class TestGuardExplicitUserConfirmationRequirement(unittest.TestCase):
    
    @patch('my_app.domain.FlightBookingApi')
    def test_compliance_agent_details_flight_changes(self, MockApi):
        """
        Test compliance: Agent details flight changes for reservation ID 6A7BC economy cabin from NYC to SFO both flights, and receives a confirmation 'yes' from user before proceeding.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Constructing the request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='6A7BC',
            cabin='economy',
            flights=[Flight2(flight_number='NYC-SFO', date='2024-05-01')],
            payment_id='credit_card_123456'
        )

        # Call the function under test
        guard_update_reservation_flights(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_agent_attempts_modify_without_informing(self, MockApi):
        """
        Test violation: The agent attempts to modify booking DF4321 without informing the user about the amount that will be charged using payment_id 'credit_card_7815826' and neither secures explicit consent, violating the explicit consent requirement.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False

        # Constructing the request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='DF4321',
            cabin='economy',
            flights=[Flight2(flight_number='NYC-SFO', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )

        # Call the function under test and expect a PolicyViolationException
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_compliance_agent_updates_reservation(self, MockApi):
        """
        Test compliance: Agent updates reservation PIX123, stating and maintaining cabin type economy across segments, and confirming with user changes and using payment_id 'gift_card_46129'. Receives explicit confirmation before changing.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Constructing the request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='PIX123',
            cabin='economy',
            flights=[Flight2(flight_number='JFK-LAX', date='2024-06-01')],
            payment_id='gift_card_46129'
        )

        # Call the function under test
        guard_update_reservation_flights(args, history, api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_agent_changes_flights_without_confirmation(self, MockApi):
        """
        Test violation: Agent changes flights and cabin from economy to first class for reservation AA471, without checking consistency across all segments and without receiving explicit user confirmation.
        """
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = False

        # Constructing the request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='AA471',
            cabin='first_class',
            flights=[Flight2(flight_number='LAX-JFK', date='2024-07-01')],
            payment_id='credit_card_123456'
        )

        # Call the function under test and expect a PolicyViolationException
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, history, api)


if __name__ == '__main__':
    unittest.main()
