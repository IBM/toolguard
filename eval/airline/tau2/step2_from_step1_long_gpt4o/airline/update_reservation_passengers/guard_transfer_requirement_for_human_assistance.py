from typing import *
import airline
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_transfer_requirement_for_human_assistance(history: ChatHistory, api: I_Airline, reservation_id: str, passengers: list[Passenger | dict]):
    """
    Policy to check: Agents are instructed to transfer users to a human agent when passenger modification requests surpass the capabilities of the 'update_reservation_passengers' tool. This includes any change in passenger count or modifications not supported by the tool. Agents must confirm that all available tools have been used and that the issue cannot be resolved due to passenger number constraints before initiating the transfer.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        passengers: An array of objects containing details about each passenger.
    """
    try:
        # Get the current reservation details
        reservation = api.get_reservation_details(reservation_id)
        
        # Check if the number of passengers has changed
        if len(passengers) != len(reservation.passengers):
            raise PolicyViolationException("Passenger count change detected. Transfer to human agent required.")
        
        # Attempt to update reservation passengers
        api.update_reservation_passengers(reservation_id, passengers)
    except ValueError as e:
        # If update fails due to passenger count mismatch, transfer to human agent
        if "number of passengers does not match" in str(e):
            raise PolicyViolationException("Passenger count change detected. Transfer to human agent required.")
        else:
            raise e