from typing import *
import airline
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_validate_passenger_number_consistency(history: ChatHistory, api: I_Airline, reservation_id: str, passengers: list[Passenger | dict]):
    """
    Policy to check: When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same. You can change details like name or date of birth, but the total number must not be altered. This rule is critical and an exception cannot be made, even by human agents.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        passengers: An array of objects containing details about each passenger.
    """
    # Fetch the current reservation details using the API
    reservation_details = api.get_reservation_details(reservation_id)
    
    # Check if the number of passengers in the reservation matches the number of passengers provided
    if len(reservation_details.passengers) != len(passengers):
        raise PolicyViolationException("The number of passengers cannot be changed.")