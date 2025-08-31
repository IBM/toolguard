from unittest.mock import MagicMock
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.transfer_to_human_agents.guard_transfer_to_human_agent_conditions import guard_transfer_to_human_agent_conditions
from airline.i_airline import *
from datetime import datetime, timedelta

def test_transfer_for_reservation_details_violation():
    """
    Policy: Transfer only if explicitly requested or cannot be resolved with available tools.
    Example: "A user asks for details about their reservation ID '8JX2WO'... This violates the policy as the issue can be resolved with the available tool."
    """
    api = MagicMock(spec=I_Airline)
    # Mock dependent tools
    api.get_reservation_details.side_effect = lambda reservation_id: Reservation(
        reservation_id=reservation_id,
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="one_way",
        cabin="economy",
        flights=[],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    ) if reservation_id == "8JX2WO" else None
    api.get_flight_status.side_effect = lambda *args, **kwargs: "on time"
    api.calculate.side_effect = lambda expr: str(eval(expr))
    api.update_reservation_flights.side_effect = lambda *args, **kwargs: None
    api.search_direct_flight.side_effect = lambda *args, **kwargs: []
    api.list_all_airports.side_effect = lambda: []

    with pytest.raises(PolicyViolationException):
        guard_transfer_to_human_agent_conditions(api, summary="User requests reservation details")

def test_transfer_explicit_user_request_compliance():
    """
    Policy: Transfer only if explicitly requested or cannot be resolved with available tools.
    Example: "A user explicitly requests to be transferred to a human agent stating: 'I need to speak with a real person about my bill.'"
    """
    api = MagicMock(spec=I_Airline)
    # Mock dependent tools
    api.get_reservation_details.side_effect = lambda *args, **kwargs: None
    api.get_flight_status.side_effect = lambda *args, **kwargs: "on time"
    api.calculate.side_effect = lambda expr: str(eval(expr))
    api.update_reservation_flights.side_effect = lambda *args, **kwargs: None
    api.search_direct_flight.side_effect = lambda *args, **kwargs: []
    api.list_all_airports.side_effect = lambda: []

    # Should not raise exception
    guard_transfer_to_human_agent_conditions(api, summary="User requests assistance with billing directly from an agent")