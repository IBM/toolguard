from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_baggage_addition_policy(api: I_Airline, reservation_id: str, total_baggages: int, nonfree_baggages: int, payment_id: str):
    """
    Policy to check: When using the update_reservation_baggages tool, you can add checked bags to an existing reservation but cannot remove them. Ensure that any additional bags are reflected in both the total_baggages and nonfree_baggages fields. Verify that the bags adhere to the baggage allowance based on the user's membership status (regular, silver, gold) and cabin class (basic economy, economy, business). Calculate fees based on additional baggage, if applicable. Always use payment methods already stored in the user's profile for additional baggage fees.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'
        total_baggages: The updated total number of baggage items included in the reservation.
        nonfree_baggages: The updated number of non-free baggage items included in the reservation.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
        
    """
    pass #FIXME