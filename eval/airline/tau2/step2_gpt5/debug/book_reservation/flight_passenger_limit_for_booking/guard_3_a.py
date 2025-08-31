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

    # Validate cabin class
    if cabin not in ('business', 'economy', 'basic_economy'):
        raise PolicyViolationException("Invalid cabin class provided.")

    # Validate flights list
    if not flights or not isinstance(flights, list):
        raise PolicyViolationException("Flights information must be provided and consistent for all passengers.")

    normalized_flights = []
    for flight in flights:
        if not isinstance(flight, FlightInfo):
            try:
                flight = FlightInfo(**flight)
            except Exception:
                raise PolicyViolationException("Invalid flight information provided.")
        if not flight.flight_number or not flight.date:
            raise PolicyViolationException("Each flight must have a flight number and date.")
        normalized_flights.append((flight.flight_number, flight.date))

    if len(normalized_flights) == 0:
        raise PolicyViolationException("All passengers must share the same complete flight itinerary.")

    # Ensure all passengers have identical flight itineraries and cabin
    # Since cabin is a single argument, differing cabins would be caught above.
    # But we still check if any passenger dict/object has a different cabin or flights info (if provided)
    for p in passengers:
        if isinstance(p, dict):
            # If passenger dict contains 'cabin', ensure it matches
            if 'cabin' in p and p['cabin'] != cabin:
                raise PolicyViolationException("All passengers must have the same cabin class.")
            # If passenger dict contains 'flights', ensure it matches normalized_flights
            if 'flights' in p:
                try:
                    p_flights = [(f['flight_number'], f['date']) if isinstance(f, dict) else (f.flight_number, f.date) for f in p['flights']]
                except Exception:
                    raise PolicyViolationException("Invalid flight information for a passenger.")
                if p_flights != normalized_flights:
                    raise PolicyViolationException("All passengers must have identical flight itineraries.")
        elif isinstance(p, Passenger):
            # Passenger model doesn't have cabin or flights info, so nothing to check here
            pass
        else:
            raise PolicyViolationException("Invalid passenger information provided.")