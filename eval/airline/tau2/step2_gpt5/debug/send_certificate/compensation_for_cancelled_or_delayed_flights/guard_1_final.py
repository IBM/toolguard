from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_compensation_for_cancelled_or_delayed_flights(api: I_Airline, user_id: str, amount: int):
    """
    Guard to enforce policy for issuing compensation certificates for cancelled or delayed flights.

    Policy:
        - Only silver/gold members, or those with travel insurance, or those traveling in business class are eligible.
        - Compensation amounts:
            * $100 per passenger for cancellations.
            * $50 per passenger for delays if the reservation is altered as requested by the user.
        - Must verify membership, insurance, cabin class, and flight status before issuing.
        - Do not compensate if the user is a regular member, has no travel insurance, and flies economy/basic economy.
    """
    # Get user details
    user = api.get_user_details(user_id)

    # Check eligibility criteria
    eligible_membership = user.membership in ["silver", "gold"]

    # Iterate over reservations to find affected flights
    eligible = False
    for res_id in user.reservations:
        reservation = api.get_reservation_details(res_id)
        has_insurance = reservation.insurance == "yes"
        business_class = reservation.cabin == "business"

        # Check if user meets at least one eligibility criterion
        if not (eligible_membership or has_insurance or business_class):
            continue

        # Check flight statuses in the reservation
        for flight in reservation.flights:
            status = api.get_flight_status(flight.flight_number, flight.date)
            if status == "cancelled":
                expected_amount = 100 * len(reservation.passengers)
                if amount != expected_amount:
                    raise PolicyViolationException(
                        f"Invalid amount for cancellation. Expected ${expected_amount}"
                    )
                eligible = True
            elif status == "delayed":
                expected_amount = 50 * len(reservation.passengers)
                if amount != expected_amount:
                    raise PolicyViolationException(
                        f"Invalid amount for delay. Expected ${expected_amount}"
                    )
                eligible = True

    if not eligible:
        raise PolicyViolationException(
            "User is not eligible for compensation under the policy."
        )