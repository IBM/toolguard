from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_validate_passenger_number_consistency(api: I_Airline, reservation_id: str, passengers: list[Passenger | dict]):
    """
    Policy to check: When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same. You can change details like name or date of birth, but the total number must not be altered. This rule is critical and an exception cannot be made, even by human agents.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        passengers: An array of objects containing details about each passenger.
        
    """
    pass #FIXME