from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_cabin_uniformity_requirement(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Cabin class must be the same across all flights in a reservation.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Ensure that all flights in the provided list have the same cabin class as the provided `cabin` argument.
    # Since FlightInfo does not contain cabin info, we must compare against the intended cabin for the update.
    # The policy states that all flights in the reservation must have the same cabin class.

    # If flights list is empty, nothing to check.
    if not flights:
        return

    # Check that all flights are intended to be in the same cabin class.
    # Since the `cabin` parameter represents the intended cabin for the whole reservation,
    # any deviation from this uniform cabin class would violate the policy.
    for flight in flights:
        # In this context, we assume that the cabin class for each flight in the update
        # must match the provided `cabin` argument. If any mismatch is found, raise violation.
        # If flight is a dict and contains a 'cabin' key, check it.
        if isinstance(flight, dict) and 'cabin' in flight:
            if flight['cabin'] != cabin:
                raise PolicyViolationException(
                    "Cabin class must be the same across all flights in a reservation."
                )
        # If flight is a FlightInfo object, it should not have a cabin attribute, so no check here.
        # The uniformity is enforced by the `cabin` argument for all flights.

    # Additionally, verify against existing reservation details to ensure no mixed cabins.
    reservation = api.get_reservation_details(reservation_id)
    if reservation.cabin != cabin:
        # If the reservation's current cabin differs from the intended cabin,
        # ensure that all flights are being updated to the new cabin.
        # This is already implied by the `cabin` argument, so no further check needed here.
        pass

    # If we reach here, the cabin uniformity requirement is satisfied.