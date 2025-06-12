import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.update_reservation_flights.guard_update_reservation_flights import guard_update_reservation_flights
from my_app.common import *
from my_app.domain import *


class TestGuardBasicEconomyFlightModificationProhibition(unittest.TestCase):
    """Tests for the guard_update_reservation_flights function."""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        
        history = MagicMock()
        history.ask_bool.return_value = True

        api:FlightBookingApi = MagicMock()

        api.get_flight_details = MagicMock() 
        def get_flight_side_effect(args, **kwargs):
            if args.flight_id == "HAT001":
                return GetFlightDetailsResponse.model_construct(
                    origin="SFO",
                    destination="JFK"
                )
            if args.flight_id == "HAT002":
                return GetFlightDetailsResponse.model_construct(
                    origin="LAX",
                    destination="JFK"
                )
        api.get_flight_details.side_effect = get_flight_side_effect

        user_details = GetUserDetailsResponse.model_construct(
            payment_methods={
                'credit_card_7815826': PaymentMethods(source='credit_card', brand='Visa', last_four='1234'),
            },
            membership = "regular"
        )
        api.get_user_details.return_value = user_details

        def get_reservation_side_effect(args, **kwargs):
            if args.reservation_id=='RESRV':
                return GetReservationDetailsResponse.model_construct(
                    reservation_id='RESRV',
                    origin='SFO',
                    destination='JFK',
                    flight_type='round_trip',
                    flights=[Flight3(flight_number='HAT001', 
                                    date='2024-06-01', #change date
                                    origin='SFO', destination='JFK')],
                )
            if args.reservation_id=='LY123':
                return GetReservationDetailsResponse.model_construct(
                    reservation_id='LY123',
                    origin='LAX',
                    destination='JFK',
                    flight_type='round_trip',
                    flights=[Flight3(flight_number='HAT001', 
                                    date='2024-06-01', #change date
                                    origin='LAX', destination='JFK')],
                )
        api.get_reservation_details.side_effect = get_reservation_side_effect

        self.api = api
        self.history = history

    def test_modify_reservation_non_basic_economy(self):
        """Modifying a reservation in cabins other than 'basic economy', like 'business' or 'premium economy', such as changing flight numbers or dates, complies with the policy that restricts changes only to basic economy flights."""

        # Creating compliant request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RESRV',
            cabin='business',
            flights=[Flight2(flight_number='HAT170', date='2024-05-01')],
            payment_id='credit_card_567890'
        )

        guard_update_reservation_flights(args, self.history, self.api)

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_modify_basic_economy_flight(self, MockApi):
        """A user attempts to update a reservation with a cabin type set to 'basic economy', such as changing flight HAT170 to a different date, despite the policy prohibiting modifications to basic economy flights."""
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Creating violation request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RESRV',
            cabin='basic_economy',
            flights=[Flight2(flight_number='HAT170', date='2024-05-01')],
            payment_id='voucher_123456'
        )

        # Call the function under test and expect exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_update_reservation_flights(args, history, api)

        self.assertEqual(str(context.exception), "Basic economy flights cannot be modified.")

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_alter_basic_economy_reservation(self, MockApi):
        """Using the tool to alter a reservation with the cabin set as 'basic economy', like updating a flight number or changing cabin classes, which violates the policy."""
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Creating violation request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RESRV',
            cabin='basic_economy',
            flights=[Flight2(flight_number='HAT170', date='2024-05-01')],
            payment_id='certificate_789012'
        )

        # Call the function under test and expect exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_update_reservation_flights(args, history, api)

        self.assertEqual(str(context.exception), "Basic economy flights cannot be modified.")

    @patch('my_app.domain.FlightBookingApi')
    def test_violation_modify_with_payment_id(self, MockApi):
        """Users try to use payment methods, such as 'voucher_123456' or 'certificate_789012', to modify flight details in a 'basic economy' reservation, against policy restrictions."""
        # Mocking the API and history
        api = MockApi()
        history = MagicMock()
        history.ask_bool.return_value = True

        # Creating violation request
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RESRV',
            cabin='basic_economy',
            flights=[Flight2(flight_number='HAT170', date='2024-05-01')],
            payment_id='credit_card_998877'
        )

        # Call the function under test and expect exception
        with self.assertRaises(PolicyViolationException) as context:
            guard_update_reservation_flights(args, history, api)

        self.assertEqual(str(context.exception), "Basic economy flights cannot be modified.")


if __name__ == '__main__':
    unittest.main()
