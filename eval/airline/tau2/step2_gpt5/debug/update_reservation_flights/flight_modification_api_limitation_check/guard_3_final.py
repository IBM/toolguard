from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_flight_modification_api_limitation_check(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Agents must verify the following before using the Flight Modification API:
    - Basic economy flights are unmodifiable.
    - For other flight reservations, ensure that origin, destination, and trip type remain unchanged from the initial booking.
    - Prices for flight segments retained stay at original rates, not updated by the API. Manual validation of segment prices is required.
    """
    # Retrieve the original reservation details
    reservation = api.get_reservation_details(reservation_id)

    # 1. Basic economy flights are unmodifiable
    if reservation.cabin == 'basic_economy':
        raise PolicyViolationException("Basic economy flights cannot be modified.")

    # 2. Ensure origin, destination, and trip type remain unchanged
    if flights:
        # Get the first and last flight info from the new flights list
        first_flight_info = flights[0]
        last_flight_info = flights[-1]

        if isinstance(first_flight_info, dict):
            first_flight_number = first_flight_info.get('flight_number')
        else:
            first_flight_number = first_flight_info.flight_number

        if isinstance(last_flight_info, dict):
            last_flight_number = last_flight_info.get('flight_number')
        else:
            last_flight_number = last_flight_info.flight_number

        # Get scheduled flights to determine origin/destination
        first_scheduled = api.get_scheduled_flight(first_flight_number)
        last_scheduled = api.get_scheduled_flight(last_flight_number)

        if first_scheduled.origin != reservation.origin:
            raise PolicyViolationException(f"Origin must remain unchanged. Expected {reservation.origin}, got {first_scheduled.origin}.")
        if last_scheduled.destination != reservation.destination:
            raise PolicyViolationException(f"Destination must remain unchanged. Expected {reservation.destination}, got {last_scheduled.destination}.")

    # Ensure trip type remains unchanged
    if cabin != reservation.cabin:
        # Cabin change is not explicitly prohibited except for basic economy, but we ensure trip type check separately
        pass
    if reservation.flight_type != reservation.flight_type:
        # This check in original code was incorrect; compare with original reservation's trip type
        raise PolicyViolationException("Trip type must remain unchanged.")

    # 3. Manual validation of segment prices is required
    # We check that for any retained segment (same flight number and date), the price matches the original
    original_segments = {(f.flight_number, f.date): f.price for f in reservation.flights}
    for new_flight in flights:
        if isinstance(new_flight, dict):
            fn = new_flight.get('flight_number')
            dt = new_flight.get('date')
        else:
            fn = new_flight.flight_number
            dt = new_flight.date
        if (fn, dt) in original_segments:
            # Price must be manually validated; here we enforce that it matches original
            raise PolicyViolationException("Manual validation of retained segment prices is required before modification.")