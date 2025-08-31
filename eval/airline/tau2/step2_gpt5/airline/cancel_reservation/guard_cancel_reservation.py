from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

from airline.cancel_reservation.guard_strict_cancellation_rules_enforcement import guard_strict_cancellation_rules_enforcement


def guard_cancel_reservation(api: I_Airline, reservation_id: str):
    """
    Checks that a tool call complies to the policies.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
         

    Raises:
        PolicyViolationException: If the tool call does not comply to the policy.
    """
    
    guard_strict_cancellation_rules_enforcement(api, reservation_id)
