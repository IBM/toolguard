from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_ensure_user_confirmation(api: I_Airline, reservation_id: str, passengers: list[Passenger | dict]):
    """
    Policy to check: Before using ToolX to update passenger information in the booking database, 
    an airline agent must present the details of the changes to the user and obtain explicit confirmation ('yes') 
    from them before proceeding.

    Args:
        api (I_Airline): API to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        passengers: An array of objects containing details about each passenger.
    """
    # Retrieve the current reservation details to compare existing passengers with the new list
    current_reservation = api.get_reservation_details(reservation_id)
    current_passengers = current_reservation.passengers

    # If there is any change in passenger details, confirmation is required
    if current_passengers != passengers:
        # In a real scenario, confirmation would be obtained from the user.
        # Here, we simulate the check by requiring a special marker in passengers to indicate confirmation.
        # For example, the last passenger dict could contain a key '__user_confirmed__': 'yes'.
        confirmed = False
        for p in passengers:
            if isinstance(p, dict) and p.get('__user_confirmed__', '').lower() == 'yes':
                confirmed = True
                break
        if not confirmed:
            raise PolicyViolationException(
                "Explicit user confirmation ('yes') is required before updating passenger information."
            )