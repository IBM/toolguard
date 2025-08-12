from typing import *
import airline
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_payment_method_validation_for_baggage_update(history: ChatHistory, api: I_Airline, reservation_id: str, total_baggages: int, nonfree_baggages: int, payment_id: str):
    """
    Policy to check: Ensure the payment method used is stored in the user's profile before using the 'update_reservation_baggages' tool. Verify the payment method's existence first to maintain transaction security, preventing unauthorized use. This step is crucial for baggage updates.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'
        total_baggages: The updated total number of baggage items included in the reservation.
        nonfree_baggages: The updated number of non-free baggage items included in the reservation.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    try:
        # Retrieve reservation details using the API
        reservation_details = api.get_reservation_details(reservation_id)
        if reservation_details is None:
            raise PolicyViolationException("Reservation details could not be retrieved.")
    except ValueError:
        raise PolicyViolationException("Reservation details could not be retrieved.")

    try:
        # Retrieve user details using the API
        user_details = api.get_user_details(reservation_details.user_id)
        if user_details is None:
            raise PolicyViolationException("User details could not be retrieved.")
    except ValueError:
        raise PolicyViolationException("User details could not be retrieved.")

    # Check if the payment method is stored in the user's profile
    if payment_id not in user_details.payment_methods:
        raise PolicyViolationException("Payment method is not stored in the user's profile.")

    # Check the number of gift cards used
    gift_card_count = sum(1 for method in user_details.payment_methods.values() if method.source == 'gift_card')
    if gift_card_count > 3:
        raise PolicyViolationException("Exceeded the allowed limit of gift cards.")

    # Check if multiple certificates are used
    certificate_count = sum(1 for method in user_details.payment_methods.values() if method.source == 'certificate')
    if certificate_count > 1:
        raise PolicyViolationException("Exceeded the allowed limit of certificates.")

    # Ensure only one credit card is used
    credit_card_count = sum(1 for method in user_details.payment_methods.values() if method.source == 'credit_card')
    if credit_card_count > 1:
        raise PolicyViolationException("Exceeded the allowed limit of credit cards.")