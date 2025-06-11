import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.book_reservation.check_Booking_Information_Collection import check_Booking_Information_Collection
from my_app.common import *
from my_app.domain import *


class TestBookingInformationCollectionCompliance(unittest.TestCase):
    """Tests for compliance with the Booking Information Collection policy."""

    def test_compliance_user_id_trip_type_iata_codes(self):
        """
        The agent properly collects the user's ID 'john_doe_123', specifies the trip type as 'one_way', and uses the IATA codes 'SFO' for origin and 'JFK' for destination before initiating the reservation.
        """
        # Mocking dependencies
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct()
        airports = ListAllAirportsResponse.model_construct(root={"SFO": "San Francisco", "JFK": "New York"})

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.list_all_airports.return_value = airports

        # Function call arguments
        args = BookReservationRequest(
            user_id='john_doe_123',
            origin='SFO',
            destination='JFK',
            flight_type='one_way',
            cabin='economy',
            flights=[Flight(flight_number="FL123", date="2024-05-01")],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01")
            ],
            payment_methods=[
                PaymentMethod(payment_id="asas", amount=39)
            ],
            total_baggages=0,
            nonfree_baggages=0,
            insurance='no'
        )

        # Invoke function under test
        check_Booking_Information_Collection(args, history, api)


class TestBookingInformationCollectionViolation(unittest.TestCase):
    """Tests for violation of the Booking Information Collection policy."""

    def test_violation_missing_user_id(self):
        """
        An agent attempts to book a reservation without collecting the user ID, providing only the origin and destination, resulting in an incomplete reservation request.
        """
        # Mocking dependencies
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct()
        airports = ListAllAirportsResponse.model_construct(root={"SFO": "San Francisco", "JFK": "New York"})

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.list_all_airports.return_value = airports

        # Function call arguments
        args = BookReservationRequest(
            user_id='',  # Missing user ID
            origin='SFO',
            destination='JFK',
            flight_type='one_way',
            cabin='economy',
            flights=[Flight(flight_number="FL123", date="2024-05-01")],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01")
            ],
            payment_methods=[
                PaymentMethod(payment_id="asas", amount=39)
            ],
            total_baggages=0,
            nonfree_baggages=0,
            insurance='no'
        )

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException):
            check_Booking_Information_Collection(args, history, api)


    def test_violation_missing_trip_type(self):
        """
        The agent does not specify the trip type, whether one-way or round-trip, and proceeds to book a flight with only the user's ID, origin, and destination.
        """
        # Mocking dependencies
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct()
        airports = ListAllAirportsResponse.model_construct(root={"SFO": "San Francisco", "JFK": "New York"})

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.list_all_airports.return_value = airports

        # Function call arguments
        args = BookReservationRequest.model_construct(
            user_id='john_doe_123',
            origin='SFO',
            destination='JFK',
            flight_type='',  # Missing trip type
            cabin='economy',
            flights=[Flight(flight_number="FL123", date="2024-05-01")],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01")
            ],
            payment_methods=[
                PaymentMethod(payment_id="asas", amount=39)
            ],
            total_baggages=0,
            nonfree_baggages=0,
            insurance='no'
        )

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException):
            check_Booking_Information_Collection(args, history, api)


    def test_violation_missing_origin_iata_code(self):
        """
        An agent initiates a reservation with the user_id and destination but forgets to provide the IATA code for the origin, thus failing to comply with the requirement to specify both departure and arrival locations.
        """
        # Mocking dependencies
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct()
        airports = ListAllAirportsResponse.model_construct(root={"SFO": "San Francisco", "JFK": "New York"})

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.list_all_airports.return_value = airports

        # Function call arguments
        args = BookReservationRequest(
            user_id='john_doe_123',
            origin='',  # Missing origin IATA code
            destination='JFK',
            flight_type='one_way',
            cabin='economy',
            flights=[Flight(flight_number="FL123", date="2024-05-01")],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01")
            ],
            payment_methods=[
                PaymentMethod(payment_id="asas", amount=39)
            ],
            total_baggages=0,
            nonfree_baggages=0,
            insurance='no'
        )

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException):
            check_Booking_Information_Collection(args, history, api)


    def test_violation_non_iata_origin_code(self):
        """
        The agent attempts to book a flight reservation but provides a non-IATA code for the origin, like 'San Francisco' instead of 'SFO', resulting in an invalid input format.
        """
        # Mocking dependencies
        history = MagicMock()
        history.ask_bool.return_value = True

        user_details = GetUserDetailsResponse.model_construct()
        airports = ListAllAirportsResponse.model_construct(root={"SFO": "San Francisco", "JFK": "New York"})

        api = MagicMock()
        api.get_user_details.return_value = user_details
        api.list_all_airports.return_value = airports

        # Function call arguments
        args = BookReservationRequest(
            user_id='john_doe_123',
            origin='San Francisco',  # Non-IATA origin code
            destination='JFK',
            flight_type='one_way',
            cabin='economy',
            flights=[Flight(flight_number="FL123", date="2024-05-01")],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01")
            ],
            payment_methods=[
                PaymentMethod(payment_id="asas", amount=39)
            ],
            total_baggages=0,
            nonfree_baggages=0,
            insurance='no'
        )

        # Invoke function under test and expect exception
        with self.assertRaises(PolicyViolationException):
            check_Booking_Information_Collection(args, history, api)


if __name__ == '__main__':
    unittest.main()
