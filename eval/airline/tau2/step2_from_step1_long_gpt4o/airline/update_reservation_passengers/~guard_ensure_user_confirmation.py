from typing import *
import airline
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_ensure_user_confirmation(history: ChatHistory, api: I_Airline, reservation_id: str, passengers: list[Passenger | dict]):
    """
    Policy to check: Before using ToolX to update passenger information in the booking database, an airline agent must present the details of the changes to the user and obtain explicit confirmation ('yes') from them before proceeding.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        passengers: An array of objects containing details about each passenger.
    """
    # Retrieve reservation details
    reservation_details = api.get_reservation_details(reservation_id)
    
    # Check if the user has confirmed the changes
    confirmation_question = f"Did the user confirm the changes to the passenger information for reservation {reservation_id}?"
    user_confirmed = history.ask_bool(confirmation_question)
    
    if not user_confirmed:
        raise PolicyViolationException("User did not provide explicit 'yes' confirmation for updating passenger information.")