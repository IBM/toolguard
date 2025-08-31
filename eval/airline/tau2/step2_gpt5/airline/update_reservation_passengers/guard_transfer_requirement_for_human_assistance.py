from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_transfer_requirement_for_human_assistance(api: I_Airline, reservation_id: str, passengers: list[Passenger | dict]):
    """
    Policy to check: Agents are instructed to transfer users to a human agent when passenger modification requests surpass 
    the capabilities of the 'update_reservation_passengers' tool. This includes any change in passenger count or modifications 
    not supported by the tool. Agents must confirm that all available tools have been used and that the issue cannot be resolved 
    due to passenger number constraints before initiating the transfer.

    Args:
        api (I_Airline): API to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        passengers: An array of objects containing details about each passenger.
    """
    # Retrieve the current reservation details to compare passenger count
    reservation = api.get_reservation_details(reservation_id)
    current_passenger_count = len(reservation.passengers)
    new_passenger_count = len(passengers)

    # If passenger count changes, it surpasses the capabilities of 'update_reservation_passengers'
    if current_passenger_count != new_passenger_count:
        raise PolicyViolationException(
            "Passenger count change detected. Must transfer to a human agent as per policy requirements."
        )