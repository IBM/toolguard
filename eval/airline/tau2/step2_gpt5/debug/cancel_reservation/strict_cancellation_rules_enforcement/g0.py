from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_strict_cancellation_rules_enforcement(api: I_Airline, reservation_id: str):
    """
    Policy to check: The policy requires ensuring compliance with the cancellation rules before using 'cancel_reservation'. Agents must check if reservations meet these conditions: cancelled by the airline, within 24 hours of booking, or if travel insurance applies due to health or weather. Partial cancellations are prohibited. Transfer to human agents if these rules cannot facilitate cancellation.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        
    """
    pass #FIXME