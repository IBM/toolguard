from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_passengers.guard_validate_passenger_number_consistency import guard_validate_passenger_number_consistency
from airline.airline_types import *
from airline.i_airline import *

def test_update_passenger_details_same_count():
    """ 
    Policy: "When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same."
    Example: "A user updates the reservation 'ZFA04Y', originally for 3 passengers, by changing the name and date of birth of a passenger while maintaining the total number unchanged."
    """
    
    # mock other tools function return values
    original_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alice", last_name="Brown", dob="2000-07-07")
    ]
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[],
        passengers=original_passengers,
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None
    
    updated_passengers = [
        Passenger(first_name="Johnathan", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alice", last_name="Brown", dob="2000-07-07")
    ]
    
    #invoke function under test.
    guard_validate_passenger_number_consistency(api, reservation_id="ZFA04Y", passengers=updated_passengers)

def test_reduce_passenger_count_raises():
    """ 
    Policy: "When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same."
    Example: "A user attempts to update a reservation with ID 'ZFA04Y', initially having 3 passengers, to an updated list containing only 2 passengers."
    """
    
    original_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alice", last_name="Brown", dob="2000-07-07")
    ]
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[],
        passengers=original_passengers,
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None
    
    updated_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05")
    ]
    
    with pytest.raises(PolicyViolationException):
        guard_validate_passenger_number_consistency(api, reservation_id="ZFA04Y", passengers=updated_passengers)

def test_increase_passenger_count_raises():
    """ 
    Policy: "When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same."
    Example: "A user tries to modify the reservation 'ZFA04Y' by adding a fourth passenger when the reservation originally included 3 passengers."
    """
    
    original_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alice", last_name="Brown", dob="2000-07-07")
    ]
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[],
        passengers=original_passengers,
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None
    
    updated_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alice", last_name="Brown", dob="2000-07-07"),
        Passenger(first_name="Bob", last_name="White", dob="1995-09-09")
    ]
    
    with pytest.raises(PolicyViolationException):
        guard_validate_passenger_number_consistency(api, reservation_id="ZFA04Y", passengers=updated_passengers)

def test_modify_passenger_ages_same_count():
    """ 
    Policy: "When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same."
    Example: "User modifies passenger ages in the reservation with ID 'ZFA04Y', containing 4 passengers, ensuring no passenger is added or removed."
    """
    
    original_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05"),
        Passenger(first_name="Alice", last_name="Brown", dob="2000-07-07"),
        Passenger(first_name="Bob", last_name="White", dob="1995-09-09")
    ]
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[],
        passengers=original_passengers,
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None
    
    updated_passengers = [
        Passenger(first_name="John", last_name="Doe", dob="1991-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1986-05-05"),
        Passenger(first_name="Alice", last_name="Brown", dob="2001-07-07"),
        Passenger(first_name="Bob", last_name="White", dob="1996-09-09")
    ]
    
    guard_validate_passenger_number_consistency(api, reservation_id="ZFA04Y", passengers=updated_passengers)