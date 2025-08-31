from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_flight_passenger_limit_for_booking(
    api: I_Airline,
    user_id: str,
    origin: str,
    destination: str,
    flight_type: Literal['round_trip', 'one_way'],
    cabin: Literal['business', 'economy', 'basic_economy'],
    flights: list[FlightInfo],
    passengers: list[Passenger | dict],
    payment_methods: list[Payment | dict],
    total_baggages: int,
    nonfree_baggages: int,
    insurance: Literal['yes', 'no']
):
    """
    Policy to check: A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin.
    """
    # Check passenger limit
    if len(passengers) > 5:
        raise PolicyViolationException("A reservation can have at most five passengers.")

    # Ensure all passengers have the same flights and cabin
    # Since 'flights' and 'cabin' are provided for the reservation as a whole,
    # we just need to ensure that the policy is not violated by having different itineraries or cabins.
    # In this context, if flights or cabin differ per passenger, it would be represented differently in the API call.
    # Here, we validate that the provided flights list is consistent and non-empty.
    if not flights or not isinstance(flights, list):
        raise PolicyViolationException("Flights information must be provided and consistent for all passengers.")

    # All passengers must have the same cabin (already given as a single argument for the reservation)
    # But we still check that cabin is valid
    if cabin not in ('business', 'economy', 'basic_economy'):
        raise PolicyViolationException("Invalid cabin class provided.")

    # All passengers must fly the same flights: ensure no passenger-specific flight info is different
    # Since passengers are given as Passenger or dict without flight info, the only way to violate this
    # would be if flights list is inconsistent in length or content.
    # We check that all flights have required fields.
    for flight in flights:
        if not isinstance(flight, FlightInfo):
            try:
                flight = FlightInfo(**flight)
            except Exception:
                raise PolicyViolationException("Invalid flight information provided.")
        if not flight.flight_number or not flight.date:
            raise PolicyViolationException("Each flight must have a flight number and date.")