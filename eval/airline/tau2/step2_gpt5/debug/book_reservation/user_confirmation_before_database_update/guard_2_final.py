from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_user_confirmation_before_database_update(
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
    insurance: Literal['yes', 'no'],
    user_confirmation: Optional[str] = None
):
    """
    Policy to check: Ensure that before using ToolX for database updates related to booking a reservation, 
    changing flight details, passenger information, baggage edits, or cabin upgrades, you must present the 
    details of these actions to the user and obtain a clear affirmative confirmation ('yes') from the user 
    before proceeding.

    Args:
        api (I_Airline): API to access other tools.
        user_id: The ID of the user to book the reservation.
        origin: The IATA code for the origin city.
        destination: The IATA code for the destination city.
        flight_type: The type of flight.
        cabin: The cabin class.
        flights: Details about each flight.
        passengers: Details about each passenger.
        payment_methods: Details about each payment method.
        total_baggages: Total number of baggage items.
        nonfree_baggages: Number of non-free baggage items.
        insurance: Whether the reservation has insurance.
        user_confirmation: Explicit confirmation from the user ('yes' required to proceed).

    Raises:
        PolicyViolationException: If explicit 'yes' confirmation is not provided.
    """
    # Ensure explicit confirmation is provided and is exactly 'yes' (case-insensitive, ignoring whitespace)
    if not user_confirmation or user_confirmation.strip().lower() != 'yes':
        raise PolicyViolationException(
            "Explicit 'yes' confirmation from the user is required before proceeding with database updates."
        )