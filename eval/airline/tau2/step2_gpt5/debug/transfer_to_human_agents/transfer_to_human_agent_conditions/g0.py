from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_transfer_to_human_agent_conditions(api: I_Airline, summary: str):
    """
    Policy to check: Transfer a user to a human agent only if the user explicitly requests this transfer or if the problem cannot be resolved using available tools and policies within the scope of your actions. Include a summary of the user's issue when making the transfer.

    Args:
        api (I_Airline): api to access other tools.
        summary: A summary of the user's issue.
        
    """
    pass #FIXME