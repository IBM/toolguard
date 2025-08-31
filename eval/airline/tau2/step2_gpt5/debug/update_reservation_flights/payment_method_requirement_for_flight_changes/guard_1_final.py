from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_payment_method_requirement_for_flight_changes(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method. Without this, flight changes cannot be processed.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Retrieve reservation details to get the user_id
    reservation = api.get_reservation_details(reservation_id)
    user_id = reservation.user_id

    # Retrieve user details to check payment methods
    user = api.get_user_details(user_id)

    # Check if the provided payment_id exists in the user's payment methods
    payment_method = user.payment_methods.get(payment_id)
    if payment_method is None:
        raise PolicyViolationException("Provided payment method is not linked to the user's profile.")

    # Ensure the payment method is either a gift card or a credit card
    if payment_method.source not in ('gift_card', 'credit_card'):
        raise PolicyViolationException("Payment method must be a valid gift card or credit card from the user's profile.")