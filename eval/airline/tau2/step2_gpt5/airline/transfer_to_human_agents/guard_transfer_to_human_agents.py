from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

from airline.transfer_to_human_agents.guard_transfer_to_human_agent_conditions import guard_transfer_to_human_agent_conditions
from airline.transfer_to_human_agents.guard_flight_segment_transfer_condition import guard_flight_segment_transfer_condition
from airline.transfer_to_human_agents.guard_human_agent_assistance_limitation import guard_human_agent_assistance_limitation


def guard_transfer_to_human_agents(api: I_Airline, summary: str):
    """
    Checks that a tool call complies to the policies.

    Args:
        api (I_Airline): api to access other tools.
        summary: A summary of the user's issue.
         

    Raises:
        PolicyViolationException: If the tool call does not comply to the policy.
    """
    
    guard_transfer_to_human_agent_conditions(api, summary)
    guard_flight_segment_transfer_condition(api, summary)
    guard_human_agent_assistance_limitation(api, summary)
