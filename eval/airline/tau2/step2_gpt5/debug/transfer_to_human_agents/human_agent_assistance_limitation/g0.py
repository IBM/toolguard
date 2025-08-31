from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_human_agent_assistance_limitation(api: I_Airline, summary: str):
    """
    Policy to check: For requests involving changes to the number of passengers in a reservation, notify the user that neither the automated system nor human agents can process this change. Therefore, transfer to a human agent is not permitted for these requests.

    Args:
        api (I_Airline): api to access other tools.
        summary: A summary of the user's issue.
        
    """
    pass #FIXME