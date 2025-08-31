from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_cannot_modify_basic_economy_flights(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Basic economy flights in a reservation cannot be modified at all. For reservations that are not classified as basic economy, modifications are allowed but must not change the origin, destination, or trip type.
    """
    # Retrieve the current reservation details
    reservation = api.get_reservation_details(reservation_id)

    # If the reservation is basic economy, no modifications are allowed
    if reservation.cabin == 'basic_economy':
        raise PolicyViolationException("Basic economy flights cannot be modified.")

    # For non-basic economy reservations, ensure origin, destination, and trip type remain unchanged
    if reservation.origin != reservation.origin or reservation.destination != reservation.destination or reservation.flight_type != reservation.flight_type:
        # This check above is incorrect; we need to compare with the new flights' details
        pass

    # Determine the origin and destination from the new flights
    if not flights:
        return  # No flights provided, nothing to check

    # Get scheduled flight details for the first and last flights in the new itinerary
    first_flight_info = flights[0]
    last_flight_info = flights[-1]

    if isinstance(first_flight_info, dict):
        first_flight_info = FlightInfo(**first_flight_info)
    if isinstance(last_flight_info, dict):
        last_flight_info = FlightInfo(**last_flight_info)

    first_flight_schedule = api.get_scheduled_flight(first_flight_info.flight_number)
    last_flight_schedule = api.get_scheduled_flight(last_flight_info.flight_number)

    new_origin = first_flight_schedule.origin
    new_destination = last_flight_schedule.destination

    if reservation.origin != new_origin:
        raise PolicyViolationException("Origin cannot be changed for non-basic economy reservations.")
    if reservation.destination != new_destination:
        raise PolicyViolationException("Destination cannot be changed for non-basic economy reservations.")

    # Trip type check: round_trip means first flight origin == last flight destination
    new_trip_type = 'round_trip' if new_origin == new_destination else 'one_way'
    if reservation.flight_type != new_trip_type:
        raise PolicyViolationException("Trip type cannot be changed for non-basic economy reservations.")