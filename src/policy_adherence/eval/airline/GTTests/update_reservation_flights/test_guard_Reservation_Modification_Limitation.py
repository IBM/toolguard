import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.update_reservation_flights.guard_update_reservation_flights import guard_update_reservation_flights
from my_app.common import *
from my_app.domain import *


class TestReservationModificationLimitationCompliance(unittest.TestCase):
    """Test cases for compliance with reservation modification limitations."""
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        
        history = MagicMock()
        history.ask_bool.return_value = True

        api:FlightBookingApi = MagicMock()

        api.get_flight_details = MagicMock() 
        def get_flight_side_effect(args, **kwargs):
            if args.flight_id == "SFO_JFK":
                return GetFlightDetailsResponse.model_construct(
                    origin="SFO",
                    destination="JFK"
                )
            if args.flight_id == "JFK_BLA":
                return GetFlightDetailsResponse.model_construct(
                    origin="JFK",
                    destination="BLA"
                )
            if args.flight_id == "LAX_JFK":
                return GetFlightDetailsResponse.model_construct(
                    origin="LAX",
                    destination="JFK"
                )
            if args.flight_id == "LAX_BLU":
                return GetFlightDetailsResponse.model_construct(
                    origin="LAX",
                    destination="BLU"
                )
            if args.flight_id == "BLU_BLA":
                return GetFlightDetailsResponse.model_construct(
                    origin="BLU",
                    destination="BLA"
                )
            if args.flight_id == "JFK_BLA":
                return GetFlightDetailsResponse.model_construct(
                    origin="JFK",
                    destination="BLA"
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
            if args.reservation_id=='RSRV1':
                return GetReservationDetailsResponse.model_construct(
                    reservation_id='RSRV1',
                    origin='SFO',
                    destination='JFK',
                    cabin='economy',
                    flight_type='round_trip',
                    flights=[Flight3(flight_number='SFO_JFK', 
                                    date='2024-06-01', #change date
                                    origin='SFO', destination='JFK')],
                )
            if args.reservation_id=='RSRV2':
                return GetReservationDetailsResponse.model_construct(
                    reservation_id='RSRV2',
                    origin='LAX',
                    destination='JFK',
                    cabin='economy',
                    flight_type='round_trip',
                    flights=[Flight3(flight_number='LAX_JFK', 
                                    date='2024-06-01',
                                    origin='LAX', destination='JFK')],
                )
            if args.reservation_id=='RSRV2LEGS':
                return GetReservationDetailsResponse.model_construct(
                    reservation_id='RSRV2LEGS',
                    origin='LAX',
                    destination='BLA',
                    cabin='economy',
                    flight_type='round_trip',
                    flights=[Flight3(flight_number='LAX_JFK', 
                                    date='2024-06-01',
                                    origin='LAX', destination='JFK'),
                            Flight3(flight_number='JFK_BLA', 
                                    date='2024-06-01',
                                    origin='JFK', destination='BLA')],
                )
            if args.reservation_id=='RSRV_BASIC_ECONMY':
                return GetReservationDetailsResponse.model_construct(
                    reservation_id='RSRV_BASIC_ECONMY',
                    origin='SFO',
                    destination='JFK',
                    cabin='basic_economy',
                    flight_type='round_trip',
                    flights=[Flight3(flight_number='SFO_JFK', 
                                    date='2024-06-01',
                                    origin='SFO', destination='JFK')],
                )
        api.get_reservation_details.side_effect = get_reservation_side_effect

        self.api = api
        self.history = history

    def test_update_reservation_without_changing_origin_destination_trip_type(self):
        """
        An agent updates a reservation while ensuring the origin 'SFO', destination 'JFK', and 'round-trip' type remain unchanged, adhering to policy limitations.
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV1',
            cabin='economy',
            flights=[Flight2(flight_number='SFO_JFK', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )
        guard_update_reservation_flights(args, self.history, self.api)


    def test_update_reservation_with_wrong_payment(self):
        """
        An agent updates a reservation while ensuring the origin 'SFO', destination 'JFK', and 'round-trip' type remain unchanged, adhering to policy limitations.
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV1',
            cabin='economy',
            flights=[Flight2(flight_number='SFO_JFK', date='2024-05-01')],
            payment_id='weww'
        )
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, self.history, self.api)


    def test_can_update_connection(self):
        """
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV2LEGS',
            cabin='economy',
            flights=[
                Flight2(flight_number='LAX_BLU', date='2024-05-01'),
                Flight2(flight_number='BLU_BLA', date='2024-05-01'),
            ],
            payment_id='credit_card_7815826'
        )
        guard_update_reservation_flights(args, self.history, self.api)

    def test_update_reservation_with_2legs(self):
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV2LEGS',
            cabin='economy',
            flights=[
                Flight2(flight_number='LAX_JFK', date='2024-05-01'),
                Flight2(flight_number='JFK_BLA', date='2024-05-01'),
            ],
            payment_id='credit_card_7815826'
        )
        guard_update_reservation_flights(args, self.history, self.api)

    def test_update_business_reservation_without_changing_origin_destination_trip_type(self):
        """
        An agent updates a reservation while ensuring the origin 'SFO', destination 'JFK', and 'round-trip' type remain unchanged, adhering to policy limitations.
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV1',
            cabin='business',
            flights=[Flight2(flight_number='SFO_JFK', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )
        guard_update_reservation_flights(args, self.history, self.api)

    def test_change_destination_violation(self):
        """
        The agent calls 'update_reservation_flights' to change the origin airport from 'JFK' to 'LAX', violating the policy prohibiting alterations of origin and destination.
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV1',
            cabin='economy',
            flights=[Flight2(flight_number='LAX_JFK', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )

        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, self.history, self.api)


    def test_update_basic_economy_reservation(self):
        """
        An agent tries to update a basic-economy reservation
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV_BASIC_ECONMY',
            cabin='basic_economy',
            flights=[Flight2(flight_number='SFO_JFK', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, self.history, self.api)

    def test_update_to_basic_economy_reservation(self):
        """
        An agent tries to update a basic-economy reservation
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV1',
            cabin='basic_economy',
            flights=[Flight2(flight_number='SFO_JFK', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, self.history, self.api)

    
    def test_update_origin(self):
        """
        An agent tries to update a basic-economy reservation
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV1',
            cabin='basic_economy',
            flights=[Flight2(flight_number='LAX_JFK', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, self.history, self.api)

    def test_update_destination(self):
        """
        An agent tries to update a basic-economy reservation
        """
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='RSRV1',
            cabin='basic_economy',
            flights=[Flight2(flight_number='JFK_BLA', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, self.history, self.api)

if __name__ == '__main__':
    unittest.main()
