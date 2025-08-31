from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_payment_method_validation_for_baggage_update(api: I_Airline, reservation_id: str, total_baggages: int, nonfree_baggages: int, payment_id: str):
    """
    Policy to check: Ensure the payment method used is stored in the user's profile before using the 'update_reservation_baggages' tool.
    Verify the payment method's existence first to maintain transaction security, preventing unauthorized use.
    Also enforce limits: at most one travel certificate, at most one credit card, and at most three gift cards per reservation.

    Args:
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'
        total_baggages: The updated total number of baggage items included in the reservation.
        nonfree_baggages: The updated number of non-free baggage items included in the reservation.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Get reservation and user details
    reservation = api.get_reservation_details(reservation_id)
    user = api.get_user_details(reservation.user_id)

    # Check if payment method exists in user's profile
    if payment_id not in user.payment_methods:
        raise PolicyViolationException("Payment method is not stored in the user's profile.")

    # Initialize counters for payment method types
    cert_count = 0
    cc_count = 0
    gc_count = 0

    # Count existing payment methods in reservation's payment history
    for payment in reservation.payment_history:
        pm_id = payment.payment_id
        if pm_id in user.payment_methods:
            pm = user.payment_methods[pm_id]
            if pm.source == 'certificate':
                cert_count += 1
            elif pm.source == 'credit_card':
                cc_count += 1
            elif pm.source == 'gift_card':
                gc_count += 1

    # Include the new payment method in the count
    new_pm = user.payment_methods[payment_id]
    if new_pm.source == 'certificate':
        cert_count += 1
    elif new_pm.source == 'credit_card':
        cc_count += 1
    elif new_pm.source == 'gift_card':
        gc_count += 1

    # Enforce limits
    if cert_count > 1:
        raise PolicyViolationException("A reservation can use at most one travel certificate.")
    if cc_count > 1:
        raise PolicyViolationException("A reservation can use at most one credit card.")
    if gc_count > 3:
        raise PolicyViolationException("A reservation can use at most three gift cards.")