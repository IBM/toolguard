from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_passengers.guard_ensure_user_confirmation import guard_ensure_user_confirmation
from airline.airline_types import *
from airline.i_airline import *

def test_email_confirmation_before_update():
    """ 
    Policy: Before using ToolX to update passenger information in the booking database, an airline agent must present the details of the changes to the user and obtain explicit confirmation ('yes') from them before proceeding.
    Example: Before updating the passenger information for reservation 'ZFA04Y', the airline agent sends an email detailing the changes and receives a reply from the user confirming 'yes' before proceeding.
    """
    
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="one_way",
        cabin="economy",
        flights=[ReservationFlight(flight_number="HAT001", date="2024-06-01", price=300)],
        passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )

    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None

    passengers = [Passenger(first_name="John", last_name="Doe", dob="1990-01-01")]
    
    # Should not raise exception for compliance
    guard_ensure_user_confirmation(api, reservation_id="ZFA04Y", passengers=passengers)

def test_update_without_user_confirmation():
    """ 
    Policy: Before using ToolX to update passenger information in the booking database, an airline agent must present the details of the changes to the user and obtain explicit confirmation ('yes') from them before proceeding.
    Example: An airline agent updates the passenger information for a reservation without displaying the changes to the user or obtaining explicit confirmation from them, violating the policy that requires a 'yes' confirmation before proceeding.
    """
    
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="one_way",
        cabin="economy",
        flights=[ReservationFlight(flight_number="HAT001", date="2024-06-01", price=300)],
        passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )

    api = MagicMock(spec=I_Airline)
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None

    passengers = [Passenger(first_name="Jane", last_name="Smith", dob="1992-02-02")]
    
    with pytest.raises(PolicyViolationException):
        guard_ensure_user_confirmation(api, reservation_id="ZFA04Y", passengers=passengers)