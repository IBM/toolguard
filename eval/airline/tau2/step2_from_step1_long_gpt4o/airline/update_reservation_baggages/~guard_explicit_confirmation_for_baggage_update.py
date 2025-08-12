from typing import *
import airline
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_explicit_confirmation_for_baggage_update(history: ChatHistory, api: I_Airline, reservation_id: str, total_baggages: int, nonfree_baggages: int, payment_id: str):
    """
    Policy to check: Before invoking the 'update_reservation_baggages' tool to update baggage information in a reservation, ensure you list all changes and receive explicit user confirmation (yes) to proceed.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'
        total_baggages: The updated total number of baggage items included in the reservation.
        nonfree_baggages: The updated number of non-free baggage items included in the reservation.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Retrieve current reservation details
    reservation = api.get_reservation_details(reservation_id)
    
    # List all changes
    changes = f"Updating reservation '{reservation_id}' baggages: "
    changes += f"Total baggages from {reservation.total_baggages} to {total_baggages}, "
    changes += f"Non-free baggages from {reservation.nonfree_baggages} to {nonfree_baggages}, "
    changes += f"using payment method '{payment_id}'."
    
    # Ask for explicit user confirmation
    confirmation_question = f"Do you confirm the following changes? {changes}"
    user_confirmed = history.ask_bool(confirmation_question)
    
    if not user_confirmed:
        raise PolicyViolationException("Explicit user confirmation not received for baggage update.")