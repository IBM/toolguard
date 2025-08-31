from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.transfer_to_human_agents.guard_flight_segment_transfer_condition import guard_flight_segment_transfer_condition
from airline.airline_types import *
from airline.i_airline import *

def test_transfer_when_first_segment_flown():
    """
    Policy: If a user requests to cancel a trip and any segments have already been flown, transfer the user to a human agent.
    Example: A user requests to cancel their trip, and it is found that the first segment has already been flown. The system properly transfers the user's request to a human agent.
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RES123",
        user_id="USER123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[
            ReservationFlight(flight_number="FL123", date="2024-05-01", price=200),
            ReservationFlight(flight_number="FL456", date="2024-05-10", price=200)
        ],
        passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
        payment_history=[Payment(payment_id="PAY123", amount=400)],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "RES123" else None
    api.get_flight_status.side_effect = lambda flight_number, date: "landed" if (flight_number, date) == ("FL123", "2024-05-01") else "available"

    # Should not raise exception for compliance
    guard_flight_segment_transfer_condition(api, summary="User requests cancellation of trip with flown segment")

def test_violation_attempt_cancel_flown_segment():
    """
    Policy: If a user requests to cancel a trip and any segments have already been flown, transfer the user to a human agent.
    Example: The user requests to cancel a trip that has already been fully or partially flown. The system attempts to process the cancellation without transferring the user to a human agent.
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RES456",
        user_id="USER456",
        origin="LAX",
        destination="ORD",
        flight_type="one_way",
        cabin="business",
        flights=[
            ReservationFlight(flight_number="FL789", date="2024-05-02", price=500)
        ],
        passengers=[Passenger(first_name="Jane", last_name="Smith", dob="1985-05-05")],
        payment_history=[Payment(payment_id="PAY456", amount=500)],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "RES456" else None
    api.get_flight_status.side_effect = lambda flight_number, date: "landed" if (flight_number, date) == ("FL789", "2024-05-02") else "available"

    with pytest.raises(PolicyViolationException):
        guard_flight_segment_transfer_condition(api, summary="User requests cancellation without transfer despite flown segment")