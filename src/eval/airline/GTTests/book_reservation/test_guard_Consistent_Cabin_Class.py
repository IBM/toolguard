import unittest
from unittest.mock import MagicMock, patch

# Importing the function under test and necessary modules
from my_app.book_reservation.guard_book_reservation import guard_book_reservation
from my_app.common import *
from my_app.domain import *


class TestConsistentCabinClassPolicy(unittest.TestCase):
    
    @patch('my_app.domain.FlightBookingApi')
    def test_maria_and_luis_fly_economy(self, MockApi):
        """
        Test case for: Maria Gonzalez and Luis Perez both fly economy from LAX to JFK, complying with the consistent cabin class policy.
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        # Constructing the request
        args = BookReservationRequest(
            user_id='user_123',
            origin='LAX',
            destination='JFK',
            flight_type='one_way',
            cabin='economy',
            flights=[Flight(flight_number='AA123', date='2024-05-01')],
            passengers=[
                Passenger(first_name='Maria', last_name='Gonzalez', dob='1990-01-01'),
                Passenger(first_name='Luis', last_name='Perez', dob='1985-05-12')
            ],
            payment_methods=[PaymentMethod(payment_id='credit_card_123', amount=500.0)],
            total_baggages=2,
            nonfree_baggages=0,
            insurance='no'
        )

        # Mocking dependent tool
        # api.get_reservation_details.return_value = GetReservationDetailsResponse(
        #     cabin='economy'
        # )
        user = GetUserDetailsResponse.model_construct(
            name=Name(first_name="Alice", last_name="Smith"),
            email="alice.smith@example.com",
            membership="gold",
            payment_methods={
                'credit_card_123': PaymentMethods(source='credit_card', brand='Visa', last_four='1234'),
            }
        )
        api = MagicMock()
        api.get_user_details.return_value = user

        # Invoke the function under test
        guard_book_reservation(args, history, api)


if __name__ == '__main__':
    unittest.main()
