import unittest
from unittest.mock import MagicMock, patch

from my_app.update_reservation_flights.guard_update_reservation_flights import guard_update_reservation_flights
from my_app.common import *
from my_app.domain import *

class TestGuardFlightSegmentIntegrity(unittest.TestCase):
    
    @patch('my_app.update_reservation_flights.guard_update_reservation_flights.FlightBookingApi')
    def test_compliance_reservation_update_detects_flown_segment(self, MockApi):
        """
        Reservation update for ID 'DEF456' detects flown segment 'FLY789' from '2023-09-12' and correctly transfers the user to a human agent for resolution.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the return value of get_reservation_details
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            flights=[Flight3(flight_number='FLY789', date='2023-09-12', status='flown')]
        )

        # Construct the arguments
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='DEF456',
            cabin='economy',
            flights=[Flight2(flight_number='FLY789', date='2023-09-12')],
            payment_id='credit_card_1234'
        )

        # Call the function under test
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, history, api)

    @patch('my_app.update_reservation_flights.guard_update_reservation_flights.FlightBookingApi')
    def test_compliance_update_all_segments_unflown(self, MockApi):
        """
        Update for reservation ID 'GHI012' is compliant as all segments, including 'JZK001', are unflown, proceeding without issues.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the return value of get_reservation_details
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            flights=[Flight3(flight_number='JZK001', date='2023-12-01', status='scheduled')]
        )

        # Construct the arguments
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='GHI012',
            cabin='economy',
            flights=[Flight2(flight_number='JZK001', date='2023-12-01')],
            payment_id='credit_card_5678'
        )

        # Call the function under test
        try:
            guard_update_reservation_flights(args, history, api)
        except PolicyViolationException:
            self.fail("PolicyViolationException was raised unexpectedly!")

    @patch('my_app.update_reservation_flights.guard_update_reservation_flights.FlightBookingApi')
    def test_violation_update_proceeds_with_flown_segment(self, MockApi):
        """
        A user tries to update reservation ID 'ABC123' with flight segment 'FLN456', which was already flown on '2023-11-30'. Despite this violation of the Flight Segment Integrity policy, the update request proceeds without transferring the user to a human agent for assistance.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the return value of get_reservation_details
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            flights=[Flight3(flight_number='FLN456', date='2023-11-30', status='flown')]
        )

        # Construct the arguments
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='ABC123',
            cabin='economy',
            flights=[Flight2(flight_number='FLN456', date='2023-11-30')],
            payment_id='credit_card_91011'
        )

        # Call the function under test
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, history, api)

    @patch('my_app.update_reservation_flights.guard_update_reservation_flights.FlightBookingApi')
    def test_violation_update_bypasses_policy_checks(self, MockApi):
        """
        Reservation ID 'XYZ789' is updated with flight segment 'TRG789', which was already flown on '2023-10-05', violating the policy by not transferring the user to a human agent.
        """
        # Mock the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the return value of get_reservation_details
        api.get_reservation_details.return_value = GetReservationDetailsResponse.model_construct(
            flights=[Flight3(flight_number='TRG789', date='2023-10-05', status='flown')]
        )

        # Construct the arguments
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='XYZ789',
            cabin='economy',
            flights=[Flight2(flight_number='TRG789', date='2023-10-05')],
            payment_id='credit_card_121314'
        )

        # Call the function under test
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, history, api)

if __name__ == '__main__':
    unittest.main()
