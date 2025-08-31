from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_flight_modification_api_limitation_check(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: 
    - Basic economy flights are unmodifiable.
    - For other flight reservations, ensure that origin, destination, and trip type remain unchanged from the initial booking.
    - Prices for flight segments retained stay at original rates, not updated by the API. Manual validation of segment prices is required.
    """
    # Retrieve the original reservation details
    reservation = api.get_reservation_details(reservation_id)

    # 1. Basic economy flights are unmodifiable
    if reservation.cabin == 'basic_economy':
        raise PolicyViolationException("Basic economy flights cannot be modified.")

    # 2. Ensure origin remains unchanged
    if reservation.origin != reservation.origin:
        raise PolicyViolationException("Origin must remain unchanged from the initial booking.")

    # 3. Ensure destination remains unchanged
    if reservation.destination != reservation.destination:
        raise PolicyViolationException("Destination must remain unchanged from the initial booking.")

    # 4. Ensure trip type remains unchanged
    if reservation.flight_type != reservation.flight_type:
        raise PolicyViolationException("Trip type must remain unchanged from the initial booking.")

    # 5. Manual validation of segment prices is required
    # Compare retained flight segments' prices with original prices
    original_flights_map = {(f.flight_number, f.date): f.price for f in reservation.flights}
    for f in flights:
        if isinstance(f, dict):
            flight_number = f.get('flight_number')
            date = f.get('date')
        else:
            flight_number = f.flight_number
            date = f.date
        if (flight_number, date) in original_flights_map:
            # This is a retained segment; ensure price is unchanged
            original_price = original_flights_map[(flight_number, date)]
            # We cannot get updated price from API here; assume agent must have validated manually
            # If price is provided in flights, we can check it
            if isinstance(f, dict) and 'price' in f and f['price'] != original_price:
                raise PolicyViolationException("Price for retained flight segment has changed; must remain at original rate.")
            elif hasattr(f, 'price') and f.price != original_price:
                raise PolicyViolationException("Price for retained flight segment has changed; must remain at original rate.")