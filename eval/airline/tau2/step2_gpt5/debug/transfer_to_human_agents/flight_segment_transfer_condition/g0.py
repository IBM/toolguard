from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_flight_segment_transfer_condition(api: I_Airline, summary: str):
    """
    Policy to check: If a user requests to cancel a trip and any segments have already been flown, transfer the user to a human agent as the current tool cannot process partial trip cancellations.

    Args:
        api (I_Airline): api to access other tools.
        summary: A summary of the user's issue.
        
    """
    pass #FIXME