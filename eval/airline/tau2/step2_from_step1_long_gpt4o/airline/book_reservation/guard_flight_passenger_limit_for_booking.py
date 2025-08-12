from typing import *
import airline
from rt_toolguard.data_types import ChatHistory
from airline.airline_types import *
from airline.i_airline import I_Airline

class PolicyViolationException(Exception):
    pass

def guard_flight_passenger_limit_for_booking(history: ChatHistory, api: I_Airline, user_id: str, origin: str, destination: str, flight_type: Literal['round_trip', 'one_way'], cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], passengers: list[Passenger | dict], payment_methods: list[Payment | dict], total_baggages: int, nonfree_baggages: int, insurance: Literal['yes', 'no']):
    """
    Policy to check: A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        user_id: The ID of the user to book the reservation such as 'sara_doe_496'.
        origin: The IATA code for the origin city such as 'SFO'.
        destination: The IATA code for the destination city such as 'JFK'.
        flight_type: The type of flight such as 'one_way' or 'round_trip'.
        cabin: The cabin class such as 'basic_economy', 'economy', or 'business'.
        flights: An array of objects containing details about each piece of flight.
        passengers: An array of objects containing details about each passenger.
        payment_methods: An array of objects containing details about each payment method.
        total_baggages: The total number of baggage items to book the reservation.
        nonfree_baggages: The number of non-free baggage items to book the reservation.
        insurance: Whether the reservation has insurance.
    """
    # Check passenger limit
    if len(passengers) > 5:
        raise PolicyViolationException("A flight reservation can have at most five passengers.")

    # Ensure all passengers fly the same flights
    flight_numbers = {flight['flight_number'] if isinstance(flight, dict) else flight.flight_number for flight in flights}
    for passenger in passengers:
        if isinstance(passenger, dict):
            passenger_flights = passenger.get('flights', [])
        else:
            passenger_flights = getattr(passenger, 'flights', [])
        passenger_flight_numbers = {flight['flight_number'] if isinstance(flight, dict) else flight.flight_number for flight in passenger_flights}
        if passenger_flight_numbers != flight_numbers:
            raise PolicyViolationException("All passengers must fly the same flights.")

    # Ensure all passengers are in the same cabin
    for passenger in passengers:
        if isinstance(passenger, dict):
            passenger_cabin = passenger.get('cabin', None)
        else:
            passenger_cabin = getattr(passenger, 'cabin', None)
        if passenger_cabin != cabin:
            raise PolicyViolationException("All passengers must be in the same cabin.")

    # Ensure all passengers have the same flight type
    for passenger in passengers:
        if isinstance(passenger, dict):
            passenger_flight_type = passenger.get('flight_type', None)
        else:
            passenger_flight_type = getattr(passenger, 'flight_type', None)
        if passenger_flight_type != flight_type:
            raise PolicyViolationException("All passengers must have the same flight type.")