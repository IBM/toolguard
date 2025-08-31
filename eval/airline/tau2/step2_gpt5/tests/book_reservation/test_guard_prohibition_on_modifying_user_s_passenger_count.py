from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_prohibition_on_modifying_user_s_passenger_count import guard_prohibition_on_modifying_user_s_passenger_count
from airline.airline_types import *
from airline.i_airline import *

def test_update_passenger_details_without_count_change():
    """
    Policy: "The agent must not alter the number of passengers in a reservation once established, though modifications to passenger details like name or date of birth are allowed."
    Example: "An agent updates passengers' details such as name spelling, date of birth, or contact information without changing the established number of passengers in the reservation."
    """
    api = MagicMock(spec=I_Airline)
    
    # Existing reservation with 2 passengers
    existing_reservation = Reservation(
        reservation_id="RES123",
        user_id="user_001",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL123", origin="SFO", destination="JFK", date="2024-06-01", price=300)],
        passengers=[
            Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
            Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")
        ],
        payment_history=[Payment(payment_id="pay_001", amount=600)],
        created_at=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    
    api.get_reservation_details.side_effect = lambda reservation_id: existing_reservation if reservation_id == "RES123" else None
    
    updated_passengers = [
        Passenger(first_name="Johnathan", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")
    ]
    
    try:
        guard_prohibition_on_modifying_user_s_passenger_count(
            api,
            user_id="user_001",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[FlightInfo(flight_number="FL123", date="2024-06-01")],
            passengers=updated_passengers,
            payment_methods=[Payment(payment_id="pay_001", amount=600)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes"
        )
    except PolicyViolationException:
        pytest.fail("Passenger count unchanged but PolicyViolationException was raised.")

def test_attempt_to_increase_passenger_count():
    """
    Policy: "The agent must not alter the number of passengers in a reservation once established, though modifications to passenger details like name or date of birth are allowed."
    Example: "An agent attempts to alter the number of passengers in a reservation by changing the count, such as from 2 to 3, violating the policy of immutability on passenger count."
    """
    api = MagicMock(spec=I_Airline)
    
    existing_reservation = Reservation(
        reservation_id="RES123",
        user_id="user_001",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL123", origin="SFO", destination="JFK", date="2024-06-01", price=300)],
        passengers=[
            Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
            Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")
        ],
        payment_history=[Payment(payment_id="pay_001", amount=600)],
        created_at=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    
    api.get_reservation_details.side_effect = lambda reservation_id: existing_reservation if reservation_id == "RES123" else None
    
    increased_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
        Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03")
    ]
    
    with pytest.raises(PolicyViolationException):
        guard_prohibition_on_modifying_user_s_passenger_count(
            api,
            user_id="user_001",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[FlightInfo(flight_number="FL123", date="2024-06-01")],
            passengers=increased_passengers,
            payment_methods=[Payment(payment_id="pay_001", amount=600)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes"
        )

def test_attempt_to_decrease_passenger_count():
    """
    Policy: "The agent must not alter the number of passengers in a reservation once established, though modifications to passenger details like name or date of birth are allowed."
    Example: "The reservation system allows an agent to add or remove passengers, such as reducing the passenger count established from 5 to 4, thereby violating the no-alteration policy."
    """
    api = MagicMock(spec=I_Airline)
    
    existing_reservation = Reservation(
        reservation_id="RES123",
        user_id="user_001",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL123", origin="SFO", destination="JFK", date="2024-06-01", price=300)],
        passengers=[
            Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
            Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
            Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03"),
            Passenger(first_name="Jack", last_name="Daniels", dob="1980-04-04"),
            Passenger(first_name="Johnny", last_name="Walker", dob="1975-05-05")
        ],
        payment_history=[Payment(payment_id="pay_001", amount=1500)],
        created_at=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=5,
        nonfree_baggages=3,
        insurance="yes",
        status=None
    )
    
    api.get_reservation_details.side_effect = lambda reservation_id: existing_reservation if reservation_id == "RES123" else None
    
    decreased_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
        Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03"),
        Passenger(first_name="Jack", last_name="Daniels", dob="1980-04-04")
    ]
    
    with pytest.raises(PolicyViolationException):
        guard_prohibition_on_modifying_user_s_passenger_count(
            api,
            user_id="user_001",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[FlightInfo(flight_number="FL123", date="2024-06-01")],
            passengers=decreased_passengers,
            payment_methods=[Payment(payment_id="pay_001", amount=1200)],
            total_baggages=4,
            nonfree_baggages=2,
            insurance="yes"
        )