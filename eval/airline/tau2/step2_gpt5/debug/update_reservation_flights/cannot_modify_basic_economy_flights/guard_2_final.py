from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_cannot_modify_basic_economy_flights(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Basic economy flights in a reservation cannot be modified at all.
    For reservations that are not classified as basic economy, modifications are allowed
    but must not change the origin, destination, or trip type.
    """
    # Retrieve the current reservation details
    reservation = api.get_reservation_details(reservation_id)

    # If the reservation is basic economy, no modifications are allowed
    if reservation.cabin == 'basic_economy':
        raise PolicyViolationException("Basic economy flights cannot be modified.")

    # If no flights provided, nothing to check
    if not flights:
        return

    # Convert dicts to FlightInfo objects if necessary
    normalized_flights: list[FlightInfo] = []
    for f in flights:
        if isinstance(f, dict):
            normalized_flights.append(FlightInfo(**f))
        else:
            normalized_flights.append(f)

    # Get scheduled flight details for the first and last flights in the new itinerary
    first_flight_schedule = api.get_scheduled_flight(normalized_flights[0].flight_number)
    last_flight_schedule = api.get_scheduled_flight(normalized_flights[-1].flight_number)

    new_origin = first_flight_schedule.origin
    new_destination = last_flight_schedule.destination

    # Check origin and destination remain unchanged
    if reservation.origin != new_origin:
        raise PolicyViolationException("Origin cannot be changed for non-basic economy reservations.")
    if reservation.destination != new_destination:
        raise PolicyViolationException("Destination cannot be changed for non-basic economy reservations.")

    # Determine trip type from the reservation's original flights
    original_origin = reservation.origin
    original_destination = reservation.destination
    original_trip_type = 'round_trip' if original_origin == original_destination else 'one_way'

    # Determine trip type from the new flights
    new_trip_type = 'round_trip' if new_origin == new_destination else 'one_way'

    if original_trip_type != new_trip_type:
        raise PolicyViolationException("Trip type cannot be changed for non-basic economy reservations.")