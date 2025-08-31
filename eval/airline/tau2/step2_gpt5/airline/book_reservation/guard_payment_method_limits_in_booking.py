from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_payment_method_limits_in_booking(api: I_Airline, user_id: str, origin: str, destination: str, flight_type: Literal['round_trip', 'one_way'], cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo], passengers: list[Passenger | dict], payment_methods: list[Payment | dict], total_baggages: int, nonfree_baggages: int, insurance: Literal['yes', 'no']):
    """
    Policy to check: Each reservation can use at most one travel certificate, one credit card, and three gift cards.

    Args:
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
    # Count occurrences of each payment method type
    certificate_count = 0
    credit_card_count = 0
    gift_card_count = 0

    for pm in payment_methods:
        # Payment may be a dict or Payment object; ensure we can access 'source'
        if isinstance(pm, dict):
            source = pm.get('source')
        else:
            source = getattr(pm, 'source', None)

        if source == 'certificate':
            certificate_count += 1
        elif source == 'credit_card':
            credit_card_count += 1
        elif source == 'gift_card':
            gift_card_count += 1

    # Validate against policy limits
    if certificate_count > 1:
        raise PolicyViolationException("More than one travel certificate is not allowed per reservation.")
    if credit_card_count > 1:
        raise PolicyViolationException("More than one credit card is not allowed per reservation.")
    if gift_card_count > 3:
        raise PolicyViolationException("More than three gift cards are not allowed per reservation.")