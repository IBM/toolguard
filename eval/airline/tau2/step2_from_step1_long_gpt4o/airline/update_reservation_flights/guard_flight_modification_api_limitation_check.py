from typing import *
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import FlightInfo, Reservation
from airline.i_airline import I_Airline


def guard_flight_modification_api_limitation_check(history: ChatHistory, api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Agents must verify the following before using the Flight Modification API: Basic economy flights are unmodifiable. For other flight reservations, ensure that origin, destination, and trip type remain unchanged from the initial booking. Prices for flight segments retained stay at original rates, not updated by the API. Manual validation of segment prices is required.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if the a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Fetch the original reservation details
    try:
        original_reservation = api.get_reservation_details(reservation_id)
    except ValueError:
        raise PolicyViolationException("Reservation not found.")

    # Check if the cabin is basic economy
    if cabin == 'basic_economy':
        raise PolicyViolationException("Basic economy flights are unmodifiable.")

    # Validate origin, destination, and trip type
    if original_reservation.origin != flights[0].get('origin'):
        raise PolicyViolationException("Origin must remain unchanged.")
    if original_reservation.destination != flights[-1].get('destination'):
        raise PolicyViolationException("Destination must remain unchanged.")
    if original_reservation.flight_type != flights[0].get('flight_type'):
        raise PolicyViolationException("Trip type must remain unchanged.")

    # Manual validation of segment prices
    for flight in flights:
        scheduled_flight = api.get_scheduled_flight(flight['flight_number'])
        if scheduled_flight.prices[cabin] != flight.get('price'):
            raise PolicyViolationException("Prices for flight segments retained must stay at original rates.")