from unittest.mock import MagicMock
import pytest
from datetime import datetime
from rt_toolguard.data_types import PolicyViolationException
from airline.transfer_to_human_agents.guard_human_agent_assistance_limitation import guard_human_agent_assistance_limitation
from airline.i_airline import *
from airline.airline_types import *

def test_update_passenger_details_no_transfer():
    """
    Policy: For requests involving changes to the number of passengers in a reservation, transfer to a human agent is not permitted.
    Example: A user requests to update passenger details without changing the number of passengers and is not transferred to a human agent since the tool can handle the modification, adhering to the policy.
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RES123",
        user_id="USER123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL123", origin="SFO", destination="JFK", date="2024-07-01", price=300)],
        passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "RES123" else None

    # Should not raise exception
    guard_human_agent_assistance_limitation(api, summary="Update passenger passport details for RES123")

def test_modify_passenger_count_raises_violation():
    """
    Policy: For requests involving changes to the number of passengers in a reservation, transfer to a human agent is not permitted.
    Example: A user requests to change the number of passengers in a reservation and since it cannot be done via the automated system, the user is transferred to a human agent, violating the policy.
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RES456",
        user_id="USER456",
        origin="LAX",
        destination="ORD",
        flight_type="one_way",
        cabin="business",
        flights=[ReservationFlight(flight_number="FL456", origin="LAX", destination="ORD", date="2024-08-15", price=500)],
        passengers=[Passenger(first_name="Alice", last_name="Smith", dob="1985-05-05")],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "RES456" else None

    with pytest.raises(PolicyViolationException):
        guard_human_agent_assistance_limitation(api, summary="Change number of passengers from 1 to 2 for RES456")

def test_additional_passenger_transfer_violation():
    """
    Policy: For requests involving changes to the number of passengers in a reservation, transfer to a human agent is not permitted.
    Example: A customer is transferred to a human agent after attempting to add an additional passenger to their booking, which the policy clearly prohibits.
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RES789",
        user_id="USER789",
        origin="MIA",
        destination="SEA",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL789", origin="MIA", destination="SEA", date="2024-09-10", price=400)],
        passengers=[Passenger(first_name="Bob", last_name="Brown", dob="1970-12-12")],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "RES789" else None

    with pytest.raises(PolicyViolationException):
        guard_human_agent_assistance_limitation(api, summary="Add one more passenger to RES789")