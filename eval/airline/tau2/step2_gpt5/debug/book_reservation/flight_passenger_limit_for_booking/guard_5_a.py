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
    for p in passengers:
        if isinstance(p, dict):
            # Ensure passenger has required fields
            for field in ('first_name', 'last_name', 'dob'):
                if field not in p or not p[field]:
                    raise PolicyViolationException(f"Passenger missing required field: {field}.")
            # Ensure passenger's cabin matches the provided cabin
            if 'cabin' in p and p['cabin'] != cabin:
                raise PolicyViolationException("All passengers must have the same cabin class.")
            elif 'cabin' not in p:
                # If cabin not specified, assume mismatch unless explicitly matching provided cabin
                raise PolicyViolationException("All passengers must have the same cabin class.")
            # Ensure passenger's flights match normalized_flights
            if 'flights' in p:
                try:
                    p_flights = [(f['flight_number'], f['date']) if isinstance(f, dict) else (f.flight_number, f.date) for f in p['flights']]
                except Exception:
                    raise PolicyViolationException("Invalid flight information for a passenger.")
                if p_flights != normalized_flights:
                    raise PolicyViolationException("All passengers must have identical flight itineraries.")
            else:
                raise PolicyViolationException("All passengers must have identical flight itineraries.")
        elif isinstance(p, Passenger):
            # Passenger model must be assumed to share the same flights and cabin as provided in arguments
            # But we still need to ensure they match the provided cabin and flights
            # Since Passenger model doesn't have cabin/flights, we rely on provided args for uniformity
            continue
        else:
            raise PolicyViolationException("Invalid passenger information provided.")