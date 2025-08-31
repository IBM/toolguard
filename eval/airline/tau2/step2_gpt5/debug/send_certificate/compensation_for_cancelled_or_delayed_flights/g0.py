from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_compensation_for_cancelled_or_delayed_flights(api: I_Airline, user_id: str, amount: int):
    """
    Policy to check: Agents can issue compensation certificates using the `send_certificate` tool, but only for users who meet specific eligibility criteria: they must be silver/gold members, have travel insurance, or travel in business class. Compensation amounts are $100 per passenger for cancellations, and $50 per passenger for delays if the reservation is altered as requested by the user. Before sending compensation, the agent must ensure eligibility by verifying the user's membership, whether they have purchased travel insurance, the class they are flying, and the status of the flight.

    Args:
        api (I_Airline): api to access other tools.
        user_id: The ID of the user to book the reservation, such as 'sara_doe_496'.
        amount: The amount of the certificate to send.
        
    """
    pass #FIXME