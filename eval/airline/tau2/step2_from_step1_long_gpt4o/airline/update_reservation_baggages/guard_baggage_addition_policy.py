from typing import *
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_baggage_addition_policy(history: ChatHistory, api: I_Airline, reservation_id: str, total_baggages: int, nonfree_baggages: int, payment_id: str):
    """
    Policy to check: When using the update_reservation_baggages tool, you can add checked bags to an existing reservation but cannot remove them. Ensure that any additional bags are reflected in both the total_baggages and nonfree_baggages fields. Verify that the bags adhere to the baggage allowance based on the user's membership status (regular, silver, gold) and cabin class (basic economy, economy, business). Calculate fees based on additional baggage, if applicable. Always use payment methods already stored in the user's profile for additional baggage fees.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'
        total_baggages: The updated total number of baggage items included in the reservation.
        nonfree_baggages: The updated number of non-free baggage items included in the reservation.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Fetch reservation details
    reservation = api.get_reservation_details(reservation_id)
    user = api.get_user_details(reservation.user_id)

    # Check if bags are being removed
    if total_baggages < reservation.total_baggages:
        raise PolicyViolationException("Cannot remove checked bags from the reservation.")

    # Calculate free baggage allowance based on membership and cabin class
    free_bags = 0
    if user.membership == 'regular':
        if reservation.cabin == 'basic_economy':
            free_bags = 0
        elif reservation.cabin == 'economy':
            free_bags = 1
        elif reservation.cabin == 'business':
            free_bags = 2
    elif user.membership == 'silver':
        if reservation.cabin == 'basic_economy':
            free_bags = 1
        elif reservation.cabin == 'economy':
            free_bags = 2
        elif reservation.cabin == 'business':
            free_bags = 3
    elif user.membership == 'gold':
        if reservation.cabin == 'basic_economy':
            free_bags = 2
        elif reservation.cabin == 'economy':
            free_bags = 3
        elif reservation.cabin == 'business':
            free_bags = 3

    # Validate nonfree_baggages
    expected_nonfree_baggages = max(0, total_baggages - free_bags)
    if nonfree_baggages != expected_nonfree_baggages:
        raise PolicyViolationException(f"Incorrect nonfree_baggages count. Expected {expected_nonfree_baggages} based on free allowance.")

    # Validate payment method
    if payment_id not in user.payment_methods:
        raise PolicyViolationException("Payment method not stored in user profile.")

    # Calculate fees for additional baggage
    additional_bags = nonfree_baggages - reservation.nonfree_baggages
    if additional_bags > 0:
        fee = additional_bags * 50  # Assuming $50 per extra bag
        # Here you would typically check if the payment method can cover the fee, but this is a guard function

    # If all checks pass, the function completes without error