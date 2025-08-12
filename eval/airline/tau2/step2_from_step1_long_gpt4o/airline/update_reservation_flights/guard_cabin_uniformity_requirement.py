from typing import *
import airline
from rt_toolguard.data_types import ChatHistory
from airline.airline_types import *
from airline.i_airline import I_Airline

class PolicyViolationException(Exception):
    pass

def guard_cabin_uniformity_requirement(history: ChatHistory, api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Cabin class must be the same across all flights in a reservation.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if the a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Fetch reservation details using the API
    reservation_details = api.get_reservation_details(reservation_id)
    
    # Check if all flights in the reservation have the same cabin class
    for flight in reservation_details.flights:
        if flight.cabin != cabin:
            raise PolicyViolationException("Cabin class must be the same across all flights in a reservation.")