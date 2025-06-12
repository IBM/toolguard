import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.update_reservation_flights.guard_update_reservation_flights import guard_update_reservation_flights
from my_app.common import *
from my_app.domain import *


class TestGuardAPIRuleImportance(unittest.TestCase):
    
    # Compliance Test: Updating a reservation with unchanged origin and destination while ensuring the number of passengers is within the allowable limit.
    def test_update_reservation_with_unchanged_origin_destination(self):
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='ZFA04Y',
            cabin='economy',
            flights=[Flight2(flight_number='HAT001', date='2024-05-01')],
            payment_id='credit_card_7815826'
        )
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct(
            payment_methods={'credit_card_7815826': PaymentMethods(source='credit_card', brand='Visa', last_four='1234')}
        )
        reservation_details = GetReservationDetailsResponse.model_construct(
            origin='SFO',
            destination='JFK',
            flight_type='round_trip'
        )

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.get_reservation_details.return_value = reservation_details

        # Invoke the function under test
        guard_update_reservation_flights(args, history, api)

    # Compliance Test: Using one credit card registered in the user profile for the update without adding new payment options.
    def test_update_with_registered_credit_card(self):
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='ZFA04Y',
            cabin='economy',
            flights=[Flight2(flight_number='HAT002', date='2024-06-01')],
            payment_id='credit_card_7815826'
        )
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct(
            payment_methods={'credit_card_7815826': PaymentMethods(source='credit_card', brand='MasterCard', last_four='5678')}
        )
        reservation_details = GetReservationDetailsResponse.model_construct(
            origin='LAX',
            destination='ORD',
            flight_type='one_way'
        )

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.get_reservation_details.return_value = reservation_details

        # Invoke the function under test
        guard_update_reservation_flights(args, history, api)

    # Violation Test: Attempting to update a reservation where the origin changes from JFK to LAX, violating the policy that requires origin and destination to remain unchanged.
    def test_violation_origin_change(self):
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='ZFA04Y',
            cabin='economy',
            flights=[Flight2(flight_number='HAT003', date='2024-07-01')],
            payment_id='credit_card_7815826'
        )
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct(
            payment_methods={'credit_card_7815826': PaymentMethods(source='credit_card', brand='Visa', last_four='1234')}
        )
        reservation_details = GetReservationDetailsResponse.model_construct(
            origin='JFK',
            destination='LAX',
            flight_type='round_trip'
        )

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.get_reservation_details.return_value = reservation_details

        # Expecting PolicyViolationException
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, history, api)

    # Violation Test: Trying to update a reservation with seven passengers, exceeding the limit of five allowed by the policy.
    def test_violation_exceed_passenger_limit(self):
        args = UpdateReservationFlightsRequest.model_construct(
            reservation_id='ZFA04Y',
            cabin='economy',
            flights=[Flight2(flight_number='HAT004', date='2024-08-01')],
            payment_id='credit_card_7815826'
        )
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct(
            payment_methods={'credit_card_7815826': PaymentMethods(source='credit_card', brand='Visa', last_four='1234')}
        )
        reservation_details = GetReservationDetailsResponse.model_construct(
            origin='SFO',
            destination='JFK',
            flight_type='round_trip',
            passengers=[Passenger2(first_name='John', last_name='Doe', dob='1990-01-01')]*7
        )

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.get_reservation_details.return_value = reservation_details

        # Expecting PolicyViolationException
        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_flights(args, history, api)


if __name__ == '__main__':
    unittest.main()
