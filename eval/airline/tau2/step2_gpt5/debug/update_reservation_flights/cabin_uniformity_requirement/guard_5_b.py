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
    # If flights list is empty, nothing to check.
    if not flights:
        return

    # Check that all provided flights (dict type) have the same cabin class as the intended cabin.
    for flight in flights:
        if isinstance(flight, dict):
            if 'cabin' in flight and flight['cabin'] != cabin:
                raise PolicyViolationException(
                    "Cabin class must be the same across all flights in a reservation."
                )

    # Retrieve existing reservation details
    reservation = api.get_reservation_details(reservation_id)

    # Ensure all flights in the existing reservation have the same cabin as intended
    for existing_flight in reservation.flights:
        # ReservationFlight does not have a cabin attribute, so rely on reservation.cabin
        if reservation.cabin != cabin:
            raise PolicyViolationException(
                "Cabin class must be the same across all flights in a reservation."
            )

    # Also check that all provided flights (FlightInfo objects) match the intended cabin
    # Since FlightInfo does not contain cabin info, we cannot directly check them here.
    # The uniformity is ensured by checking reservation.cabin and provided dict flights above.

    # If we reach here, the cabin uniformity requirement is satisfied.