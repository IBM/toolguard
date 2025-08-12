from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_prohibition_on_modifying_user_s_passenger_count import guard_prohibition_on_modifying_user_s_passenger_count
from airline.i_airline import *
from airline.airline_types import *
from datetime import datetime, timedelta

class TestGuardProhibitionOnModifyingUsersPassengerCount:

    def test_update_passenger_details_without_changing_count(self):
        """
        Policy: "The agent must not alter the number of passengers in a reservation once established, though modifications to passenger details like name or date of birth are allowed."
        Example: "An agent updates passengers' details such as name spelling, date of birth, or contact information without changing the established number of passengers in the reservation."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API tool function return values
        reservation = Reservation(
            reservation_id="ABC123",
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-05-01", price=300)],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="pay_001", amount=300)],
            created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ABC123" else None

        # Invoke function under test.
        guard_prohibition_on_modifying_user_s_passenger_count(
            history=history,
            api=api,
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[{"flight_number": "HAT001", "date": "2024-05-01"}],
            passengers=[{"first_name": "John", "last_name": "Doe", "dob": "1990-01-01"}],
            payment_methods=[{"payment_id": "pay_001", "amount": 300}],
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes"
        )

    def test_attempt_to_change_passenger_count(self):
        """
        Policy: "The agent must not alter the number of passengers in a reservation once established, though modifications to passenger details like name or date of birth are allowed."
        Example: "An agent attempts to alter the number of passengers in a reservation by changing the count, such as from 2 to 3, violating the policy of immutability on passenger count."
        """
        
        # Mock the history service:
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API tool function return values
        reservation = Reservation(
            reservation_id="ABC123",
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-05-01", price=300)],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="pay_001", amount=300)],
            created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ABC123" else None

        # Invoke function under test.
        with pytest.raises(PolicyViolationException):
            guard_prohibition_on_modifying_user_s_passenger_count(
                history=history,
                api=api,
                user_id="sara_doe_496",
                origin="SFO",
                destination="JFK",
                flight_type="round_trip",
                cabin="economy",
                flights=[{"flight_number": "HAT001", "date": "2024-05-01"}],
                passengers=[{"first_name": "John", "last_name": "Doe", "dob": "1990-01-01"}, {"first_name": "Jane", "last_name": "Doe", "dob": "1992-02-02"}],
                payment_methods=[{"payment_id": "pay_001", "amount": 300}],
                total_baggages=2,
                nonfree_baggages=1,
                insurance="yes"
            )
