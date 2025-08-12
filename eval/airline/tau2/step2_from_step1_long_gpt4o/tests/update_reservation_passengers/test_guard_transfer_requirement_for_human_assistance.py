from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_passengers.guard_transfer_requirement_for_human_assistance import guard_transfer_requirement_for_human_assistance
from airline.i_airline import *
from airline.airline_types import *
from datetime import datetime, timedelta

class TestGuardTransferRequirementForHumanAssistance:

    def test_update_passenger_information_compliance(self):
        """
        Policy: "Agents are instructed to transfer users to a human agent when passenger modification requests surpass the capabilities of the 'update_reservation_passengers' tool."
        Example: "A user requests to update passenger information for a reservation, ensuring the passenger count remains unchanged, and the agent successfully uses 'update_reservation_passengers', complying with the tool's capabilities and policy requirements."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        api = MagicMock(spec=I_Airline)
        reservation = Reservation(reservation_id="ZFA04Y", user_id="user123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[], passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")], payment_history=[], created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"), total_baggages=2, nonfree_baggages=1, insurance="yes", status=None)
        api.get_reservation_details.return_value = reservation

        # Invoke function under test
        guard_transfer_requirement_for_human_assistance(history, api, "ZFA04Y", [Passenger(first_name="John", last_name="Doe", dob="1990-01-01")])

    def test_change_passenger_count_violation(self):
        """
        Policy: "Agents are instructed to transfer users to a human agent when passenger modification requests surpass the capabilities of the 'update_reservation_passengers' tool."
        Example: "While updating a reservation, the agent attempts to change the number of passengers, such as adding an extra passenger or reducing it, without transferring the request to a human agent for assistance, thereby violating the policy."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        api = MagicMock(spec=I_Airline)
        reservation = Reservation(reservation_id="ZFA04Y", user_id="user123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[], passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")], payment_history=[], created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"), total_baggages=2, nonfree_baggages=1, insurance="yes", status=None)
        api.get_reservation_details.return_value = reservation

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_transfer_requirement_for_human_assistance(history, api, "ZFA04Y", [Passenger(first_name="John", last_name="Doe", dob="1990-01-01"), Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")])

    def test_modify_passenger_numbers_violation(self):
        """
        Policy: "Agents are instructed to transfer users to a human agent when passenger modification requests surpass the capabilities of the 'update_reservation_passengers' tool."
        Example: "An agent handles a reservation update request to modify passenger numbers, such as from 3 to 6 or 6 to 8, without initiating a transfer to a human agent, which is required by the Transfer Requirement for Human Assistance policy."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        api = MagicMock(spec=I_Airline)
        reservation = Reservation(reservation_id="ZFA04Y", user_id="user123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[], passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01"), Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")], payment_history=[], created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"), total_baggages=2, nonfree_baggages=1, insurance="yes", status=None)
        api.get_reservation_details.return_value = reservation

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_transfer_requirement_for_human_assistance(history, api, "ZFA04Y", [Passenger(first_name="John", last_name="Doe", dob="1990-01-01")])
