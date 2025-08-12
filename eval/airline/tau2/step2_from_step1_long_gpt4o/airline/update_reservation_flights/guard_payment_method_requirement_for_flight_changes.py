from typing import *
import airline
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_payment_method_requirement_for_flight_changes(history: ChatHistory, api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method. Without this, flight changes cannot be processed.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if the a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Fetch reservation details to verify user ID
    try:
        reservation_details = api.get_reservation_details(reservation_id)
    except ValueError:
        raise PolicyViolationException("Reservation not found for the given reservation ID.")

    user_id = reservation_details.user_id

    # Fetch user details to verify payment method
    try:
        user_details = api.get_user_details(user_id)
    except ValueError:
        raise PolicyViolationException("User details not found for the given user ID.")

    if user_details is None or not user_details.payment_methods:
        raise PolicyViolationException("No payment methods found in the user's profile.")

    # Check if the provided payment_id is a valid gift card or credit card
    payment_method = user_details.payment_methods.get(payment_id)
    if payment_method is None or payment_method.source not in ['credit_card', 'gift_card']:
        raise PolicyViolationException("Invalid payment method. A valid gift card or credit card from the user's profile is required.")