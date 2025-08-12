from typing import *
import airline
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_cannot_modify_basic_economy_flights(history: ChatHistory, api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Basic economy flights in a reservation cannot be modified at all. For reservations that are not classified as basic economy, modifications are allowed but must not change the origin, destination, or trip type. It is critical for agents to verify this before invoking the update_reservation_flights tool.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if the a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Fetch the current reservation details
    reservation = api.get_reservation_details(reservation_id)

    # Check if the reservation is basic economy
    if cabin == 'basic_economy':
        raise PolicyViolationException("Basic economy flights cannot be modified.")

    # For non-basic economy reservations, ensure origin, destination, and trip type are unchanged
    for flight in flights:
        if isinstance(flight, FlightInfo):
            new_origin = flight.origin
            new_destination = flight.destination
        else:
            new_origin = flight.get('origin')
            new_destination = flight.get('destination')

        if new_origin != reservation.origin or new_destination != reservation.destination:
            raise PolicyViolationException("Origin or destination cannot be changed for non-basic economy reservations.")

    if reservation.flight_type != 'round_trip' and reservation.flight_type != 'one_way':
        raise PolicyViolationException("Trip type must remain unchanged for non-basic economy reservations.")