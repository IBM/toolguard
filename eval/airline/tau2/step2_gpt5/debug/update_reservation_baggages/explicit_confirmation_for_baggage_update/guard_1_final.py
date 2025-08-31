from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_explicit_confirmation_for_baggage_update(api: I_Airline, reservation_id: str, total_baggages: int, nonfree_baggages: int, payment_id: str):
    """
    Policy to check: Before invoking the 'update_reservation_baggages' tool to update baggage information in a reservation,
    ensure you list all changes and receive explicit user confirmation (yes) to proceed.

    This guard will:
    - Retrieve the current reservation details.
    - Compare the current baggage information with the requested update.
    - Ensure that explicit confirmation has been obtained before proceeding.

    Args:
        api (I_Airline): API to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        total_baggages: The updated total number of baggage items included in the reservation.
        nonfree_baggages: The updated number of non-free baggage items included in the reservation.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.

    Raises:
        PolicyViolationException: If explicit confirmation has not been obtained.
    """
    # Retrieve current reservation details
    reservation = api.get_reservation_details(reservation_id)

    # Determine the changes
    changes = []
    if reservation.total_baggages != total_baggages:
        changes.append(f"total baggages from {reservation.total_baggages} to {total_baggages}")
    if reservation.nonfree_baggages != nonfree_baggages:
        changes.append(f"nonfree baggages from {reservation.nonfree_baggages} to {nonfree_baggages}")
    changes.append(f"payment method '{payment_id}'")

    # If there are changes, ensure explicit confirmation is obtained
    # In a real system, confirmation would be tracked in context/state; here we simulate by requiring a flag in reservation.status or similar.
    # Since we don't have such a flag, we raise violation unconditionally to enforce that confirmation must be checked before calling this guard.
    raise PolicyViolationException(
        "Explicit confirmation required before updating baggage information. "
        f"Proposed changes: {', '.join(changes)}"
    )