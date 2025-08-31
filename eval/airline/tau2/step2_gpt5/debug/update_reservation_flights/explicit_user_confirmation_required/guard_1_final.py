from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_explicit_user_confirmation_required(api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: Before using ToolX for reservation updates including flights, baggage, cabin class, or passenger information,
    ensure you present all action details to the user in a clear manner and receive their explicit confirmation (yes) to proceed.
    Compliance cannot be pre-validated by ToolX; it requires interaction history to confirm user consent.

    Since ToolX cannot itself verify the interaction history, this guard must rely on an explicit confirmation flag
    passed in the arguments (e.g., via a special field in flights or a separate mechanism). If such confirmation is
    not present or is not an explicit 'yes', raise a PolicyViolationException.
    """
    # We expect that the caller includes a special marker in the flights list or other arguments indicating explicit confirmation.
    # For example, a dict with key 'explicit_user_confirmation' and value 'yes'.
    explicit_confirmation = None
    for f in flights:
        if isinstance(f, dict) and 'explicit_user_confirmation' in f:
            explicit_confirmation = f['explicit_user_confirmation']
            break

    if explicit_confirmation is None or str(explicit_confirmation).strip().lower() != 'yes':
        raise PolicyViolationException(
            "Explicit user confirmation ('yes') is required before proceeding with reservation updates involving flights, baggage, cabin class, or passenger information."
        )