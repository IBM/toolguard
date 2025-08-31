from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

from airline.send_certificate.guard_compensation_for_cancelled_or_delayed_flights import guard_compensation_for_cancelled_or_delayed_flights


def guard_send_certificate(api: I_Airline, user_id: str, amount: int):
    """
    Checks that a tool call complies to the policies.

    Args:
        api (I_Airline): api to access other tools.
        user_id: The ID of the user to book the reservation, such as 'sara_doe_496'.
        amount: The amount of the certificate to send.
         

    Raises:
        PolicyViolationException: If the tool call does not comply to the policy.
    """
    
    guard_compensation_for_cancelled_or_delayed_flights(api, user_id, amount)
