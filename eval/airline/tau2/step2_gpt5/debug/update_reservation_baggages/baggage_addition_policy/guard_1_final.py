from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_baggage_addition_policy(api: I_Airline, reservation_id: str, total_baggages: int, nonfree_baggages: int, payment_id: str):
    """
    Guard to enforce baggage addition policy when updating reservation baggages.
    """
    # Get current reservation details
    reservation = api.get_reservation_details(reservation_id)
    user = api.get_user_details(reservation.user_id)

    # 1. Cannot remove checked bags
    if total_baggages < reservation.total_baggages:
        raise PolicyViolationException("Cannot remove checked bags from the reservation.")

    # 2. Determine free baggage allowance based on membership and cabin class
    allowance_table = {
        'regular': {'basic_economy': 0, 'economy': 1, 'business': 2},
        'silver': {'basic_economy': 1, 'economy': 2, 'business': 3},
        'gold': {'basic_economy': 2, 'economy': 3, 'business': 3},
    }
    free_allowance = allowance_table[user.membership][reservation.cabin]

    # 3. Verify nonfree_baggages matches policy (total - free_allowance, but not less than 0)
    expected_nonfree = max(total_baggages - free_allowance, 0)
    if nonfree_baggages != expected_nonfree:
        raise PolicyViolationException(
            f"nonfree_baggages should be {expected_nonfree} based on membership and cabin allowance."
        )

    # 4. Ensure payment method is stored in user's profile if there are nonfree bags
    if nonfree_baggages > 0 and payment_id not in user.payment_methods:
        raise PolicyViolationException("Payment method must be stored in user's profile.")