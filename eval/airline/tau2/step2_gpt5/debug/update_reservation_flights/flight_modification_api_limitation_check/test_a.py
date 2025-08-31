from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_flight_modification_api_limitation_check import guard_flight_modification_api_limitation_check
from airline.airline_types import *
from airline.i_airline import *

def test_update_times_preserve_details():
    """ 
    Policy: "Agents must verify the following before using the Flight Modification API: Basic economy flights are unmodifiable. For other flight reservations, ensure that origin, destination, and trip type remain unchanged from the initial booking. Prices for flight segments retained stay at original rates, not updated by the API. Manual validation of segment prices is required."
    Example: "An agent updates a reservation by changing the flight times while preserving the original cabin class, origin, destination, and trip type, complying with the policy requirements."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="ABC123",
        user_id="user1",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="business",
        flights=[ReservationFlight(flight_number="FL123", origin="SFO", destination="JFK", date="2024-06-01", price=500)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ABC123" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(status="available", available_seats={"business": 5, "economy": 5, "basic_economy": 5}, prices={"business": 500, "economy": 300, "basic_economy": 200})

    flights = [FlightInfo(flight_number="FL123", date="2024-06-01")]
    guard_flight_modification_api_limitation_check(api, reservation_id="ABC123", cabin="business", flights=flights, payment_id="credit_card_123")

def test_basic_economy_unmodifiable():
    """ 
    Policy: "Basic economy flights are unmodifiable."
    Example: "An agent attempts to use the Flight Modification API to change the cabin class of a reservation booked under 'basic_economy'."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="BASIC1",
        user_id="user2",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="basic_economy",
        flights=[ReservationFlight(flight_number="FL124", origin="SFO", destination="JFK", date="2024-06-01", price=200)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "BASIC1" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(status="available", available_seats={"business": 5, "economy": 5, "basic_economy": 5}, prices={"business": 500, "economy": 300, "basic_economy": 200})

    flights = [FlightInfo(flight_number="FL124", date="2024-06-01")]
    with pytest.raises(PolicyViolationException):
        guard_flight_modification_api_limitation_check(api, reservation_id="BASIC1", cabin="basic_economy", flights=flights, payment_id="credit_card_123")

def test_origin_change_violation():
    """ 
    Policy: "Origin must remain unchanged."
    Example: "The agent changes the origin from 'SFO' to 'LAX' in a reservation update."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="ORIG1",
        user_id="user3",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL125", origin="SFO", destination="JFK", date="2024-06-01", price=300)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ORIG1" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(status="available", available_seats={"business": 5, "economy": 5, "basic_economy": 5}, prices={"business": 500, "economy": 300, "basic_economy": 200})

    flights = [FlightInfo(flight_number="FL126", date="2024-06-01")]
    with pytest.raises(PolicyViolationException):
        guard_flight_modification_api_limitation_check(api, reservation_id="ORIG1", cabin="economy", flights=flights, payment_id="credit_card_123")

def test_destination_change_violation():
    """ 
    Policy: "Destination must remain unchanged."
    Example: "Changing the destination from 'JFK' to 'BOS' during a reservation update."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="DEST1",
        user_id="user4",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL127", origin="SFO", destination="JFK", date="2024-06-01", price=300)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "DEST1" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(status="available", available_seats={"business": 5, "economy": 5, "basic_economy": 5}, prices={"business": 500, "economy": 300, "basic_economy": 200})

    flights = [FlightInfo(flight_number="FL128", date="2024-06-01")]
    with pytest.raises(PolicyViolationException):
        guard_flight_modification_api_limitation_check(api, reservation_id="DEST1", cabin="economy", flights=flights, payment_id="credit_card_123")

def test_trip_type_change_violation():
    """ 
    Policy: "Trip type must remain unchanged."
    Example: "An agent updates a flight reservation from a 'round_trip' to a 'one_way' trip."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="TRIP1",
        user_id="user5",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL129", origin="SFO", destination="JFK", date="2024-06-01", price=300)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "TRIP1" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(status="available", available_seats={"business": 5, "economy": 5, "basic_economy": 5}, prices={"business": 500, "economy": 300, "basic_economy": 200})

    flights = [FlightInfo(flight_number="FL130", date="2024-06-01")]
    with pytest.raises(PolicyViolationException):
        guard_flight_modification_api_limitation_check(api, reservation_id="TRIP1", cabin="economy", flights=flights, payment_id="credit_card_123")

def test_no_price_verification_violation():
    """ 
    Policy: "Manual validation of segment prices is required."
    Example: "An agent uses the API to modify a flight reservation without manually verifying the prices of retained flight segments."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="PRICE1",
        user_id="user6",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL131", origin="SFO", destination="JFK", date="2024-06-01", price=300)],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "PRICE1" else None
    api.get_flight_instance.side_effect = lambda fn, date: FlightDateStatusAvailable(status="available", available_seats={"business": 5, "economy": 5, "basic_economy": 5}, prices={"business": 600, "economy": 400, "basic_economy": 200})

    flights = [FlightInfo(flight_number="FL131", date="2024-06-01")]
    with pytest.raises(PolicyViolationException):
        guard_flight_modification_api_limitation_check(api, reservation_id="PRICE1", cabin="economy", flights=flights, payment_id="credit_card_123")