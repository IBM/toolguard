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

    # Check that all provided flights have the same cabin class as the intended cabin.
    for flight in flights:
        if isinstance(flight, dict):
            if 'cabin' in flight and flight['cabin'] != cabin:
                raise PolicyViolationException(
                    "Cabin class must be the same across all flights in a reservation."
                )

    # Verify against existing reservation details to ensure no mixed cabins.
    reservation = api.get_reservation_details(reservation_id)
    # Check all existing flights in the reservation for cabin consistency
    for existing_flight in reservation.flights:
        if reservation.cabin != cabin:
            raise PolicyViolationException(
                "Cabin class must be the same across all flights in a reservation."
            )

    # Also check that all provided flights (FlightInfo objects) match the intended cabin
    for flight in flights:
        if isinstance(flight, FlightInfo):
            # Retrieve scheduled flight details to determine available cabins
            scheduled_flight = api.get_scheduled_flight(flight.flight_number)
            # If the intended cabin is not available or mismatches, raise violation
            if cabin not in scheduled_flight.available_seats:
                raise PolicyViolationException(
                    "Cabin class must be the same across all flights in a reservation."
                )

    # If we reach here, the cabin uniformity requirement is satisfied.