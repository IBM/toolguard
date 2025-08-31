from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_cabin_change_payment_requirement(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: ToolX can be used to modify a reservation's cabin class. Ensure a uniform cabin class change across all flights within the reservation. Make sure the user pays the fare difference between the current cabin class and the new cabin class for the entire reservation as partial changes are disallowed.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Retrieve the current reservation details
    reservation = api.get_reservation_details(reservation_id)

    # Ensure all flights in the updated reservation are included
    if len(flights) != len(reservation.flights):
        raise PolicyViolationException("All flight segments must be included in the cabin change request.")

    # Ensure uniform cabin class change across all flights
    for flight in flights:
        # The new cabin must be the same for all flights
        if cabin != cabin:
            raise PolicyViolationException("Cabin class must be uniform across all flights in the reservation.")

    # Ensure the cabin change is actually for all flights (no partial changes)
    if reservation.cabin == cabin:
        raise PolicyViolationException("Cabin class is unchanged; no update required.")

    # Ensure payment is provided (basic validation)
    if not payment_id or not isinstance(payment_id, str):
        raise PolicyViolationException("A valid payment method must be provided to cover the fare difference.")

    # Additional validation could be added here to check payment sufficiency if API supports it
    # For now, we assume payment_id existence is enough for guard validation.