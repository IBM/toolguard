from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_ensure_user_confirmation(api: I_Airline, reservation_id: str, passengers: list[Passenger | dict]):
    """
    Policy to check: Before using ToolX to update passenger information in the booking database, an airline agent must present the details of the changes to the user and obtain explicit confirmation ('yes') from them before proceeding.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        passengers: An array of objects containing details about each passenger.
        
    """
    pass #FIXME