from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_prohibition_on_modifying_user_s_passenger_count(
    api: I_Airline,
    user_id: str,
    origin: str,
    destination: str,
    flight_type: Literal['round_trip', 'one_way'],
    cabin: Literal['business', 'economy', 'basic_economy'],
    flights: list[FlightInfo],
    passengers: list[Passenger | dict],
    payment_methods: list[Payment | dict],
    total_baggages: int,
    nonfree_baggages: int,
    insurance: Literal['yes', 'no']
):
    """
    Policy to check: The agent must not alter the number of passengers in a reservation once established,
    though modifications to passenger details like name or date of birth are allowed.

    This guard will fetch the existing reservation details for the user and compare the passenger count
    with the new request. If the count differs, it will raise a PolicyViolationException.
    """
    # Retrieve user details to find their reservations
    user_details = api.get_user_details(user_id)
    if not user_details.reservations:
        # No existing reservations, so no passenger count to compare against
        return

    # For simplicity, assume the policy applies to the most recent reservation
    latest_reservation_id = user_details.reservations[-1]
    existing_reservation = api.get_reservation_details(latest_reservation_id)

    # Ensure we have a valid reservation object before proceeding
    if existing_reservation is None or existing_reservation.passengers is None:
        # If reservation details are missing or passengers list is None, skip the check
        return

    existing_count = len(existing_reservation.passengers)
    new_count = len(passengers)

    if existing_count != new_count:
        raise PolicyViolationException(
            f"Passenger count change detected: existing count {existing_count}, new count {new_count}. "
            "Modifying the number of passengers in a reservation is prohibited."
        )