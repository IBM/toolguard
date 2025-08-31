from unittest.mock import MagicMock
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_passengers.guard_transfer_requirement_for_human_assistance import guard_transfer_requirement_for_human_assistance
from airline.airline_types import *
from airline.i_airline import *

def test_update_passenger_info_no_count_change():
    """ 
    Policy: Agents must transfer to a human agent only if passenger modification requests surpass the capabilities of 'update_reservation_passengers'.
    Example: A user requests to update passenger information for a reservation, ensuring the passenger count remains unchanged.
    """
    
    # Mock reservation with 2 passengers
    reservation = Reservation(
        reservation_id="ABC123",
        user_id="user_1",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[],
        passengers=[
            Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
            Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")
        ],
        payment_history=[],
        created_at="2024-05-01T10:00:00",
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )

    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ABC123" else None

    # Invoke function under test with same passenger count
    passengers_update = [
        Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
        Passenger(first_name="Jane", last_name="Smith", dob="1992-02-02")
    ]

    try:
        guard_transfer_requirement_for_human_assistance(api, reservation_id="ABC123", passengers=passengers_update)
    except PolicyViolationException:
        pytest.fail("Function raised PolicyViolationException unexpectedly when passenger count remained unchanged.")


def test_attempt_change_passenger_count_additional():
    """ 
    Policy: Must transfer to human agent if passenger count changes.
    Example: Agent attempts to change the number of passengers, such as adding an extra passenger.
    """
    
    # Mock reservation with 2 passengers
    reservation = Reservation(
        reservation_id="DEF456",
        user_id="user_2",
        origin="LAX",
        destination="ORD",
        flight_type="one_way",
        cabin="business",
        flights=[],
        passengers=[
            Passenger(first_name="Alice", last_name="Wonder", dob="1985-03-03"),
            Passenger(first_name="Bob", last_name="Builder", dob="1980-04-04")
        ],
        payment_history=[],
        created_at="2024-05-02T11:00:00",
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )

    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "DEF456" else None

    # Invoke function under test with increased passenger count
    passengers_update = [
        Passenger(first_name="Alice", last_name="Wonder", dob="1985-03-03"),
        Passenger(first_name="Bob", last_name="Builder", dob="1980-04-04"),
        Passenger(first_name="Charlie", last_name="Chaplin", dob="1975-05-05")
    ]

    with pytest.raises(PolicyViolationException):
        guard_transfer_requirement_for_human_assistance(api, reservation_id="DEF456", passengers=passengers_update)


def test_attempt_change_passenger_count_reduction():
    """ 
    Policy: Must transfer to human agent if passenger count changes.
    Example: Agent handles a reservation update request to modify passenger numbers from 3 to 2.
    """
    
    # Mock reservation with 3 passengers
    reservation = Reservation(
        reservation_id="GHI789",
        user_id="user_3",
        origin="MIA",
        destination="SEA",
        flight_type="round_trip",
        cabin="economy",
        flights=[],
        passengers=[
            Passenger(first_name="Tom", last_name="Thumb", dob="1995-06-06"),
            Passenger(first_name="Jerry", last_name="Mouse", dob="1994-07-07"),
            Passenger(first_name="Spike", last_name="Bulldog", dob="1993-08-08")
        ],
        payment_history=[],
        created_at="2024-05-03T12:00:00",
        total_baggages=3,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )

    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "GHI789" else None

    # Invoke function under test with reduced passenger count
    passengers_update = [
        Passenger(first_name="Tom", last_name="Thumb", dob="1995-06-06"),
        Passenger(first_name="Jerry", last_name="Mouse", dob="1994-07-07")
    ]

    with pytest.raises(PolicyViolationException):
        guard_transfer_requirement_for_human_assistance(api, reservation_id="GHI789", passengers=passengers_update)