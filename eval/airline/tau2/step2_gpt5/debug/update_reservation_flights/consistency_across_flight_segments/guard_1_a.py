from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_consistency_across_flight_segments(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: When updating a reservation, all flight segments must be included in the list of flights provided, 
    regardless of whether they have been altered or not.

    Args:
        api (I_Airline): API to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation.
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. 
                Even if a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    
    Raises:
        PolicyViolationException: If not all original flight segments are included in the provided flights list.
    """
    # Retrieve the original reservation details
    original_reservation = api.get_reservation_details(reservation_id)
    original_flights = original_reservation.flights

    # Normalize provided flights to FlightInfo objects if they are dicts
    provided_flights_info = []
    for f in flights:
        if isinstance(f, dict):
            provided_flights_info.append(FlightInfo(**f))
        else:
            provided_flights_info.append(f)

    # Check that all original flights are present in the provided flights list
    for orig_flight in original_flights:
        match_found = any(
            pf.flight_number == orig_flight.flight_number and pf.date == orig_flight.date
            for pf in provided_flights_info
        )
        if not match_found:
            raise PolicyViolationException(
                f"Missing original flight segment {orig_flight.flight_number} on {orig_flight.date} in the update request."
            )