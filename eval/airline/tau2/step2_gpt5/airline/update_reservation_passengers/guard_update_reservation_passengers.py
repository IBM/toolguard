from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

from airline.update_reservation_passengers.guard_ensure_user_confirmation import guard_ensure_user_confirmation
from airline.update_reservation_passengers.guard_validate_passenger_number_consistency import guard_validate_passenger_number_consistency
from airline.update_reservation_passengers.guard_transfer_requirement_for_human_assistance import guard_transfer_requirement_for_human_assistance


def guard_update_reservation_passengers(api: I_Airline, reservation_id: str, passengers: list[Passenger | dict]):
    """
    Checks that a tool call complies to the policies.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        passengers: An array of objects containing details about each passenger.
         

    Raises:
        PolicyViolationException: If the tool call does not comply to the policy.
    """
    
    guard_ensure_user_confirmation(api, reservation_id, passengers)
    guard_validate_passenger_number_consistency(api, reservation_id, passengers)
    guard_transfer_requirement_for_human_assistance(api, reservation_id, passengers)
