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
    # Look for explicit confirmation marker in the flights list or other arguments.
    explicit_confirmation = None
    for f in flights:
        if isinstance(f, dict) and f.get('explicit_user_confirmation') is not None:
            explicit_confirmation = f['explicit_user_confirmation']
            break
        elif isinstance(f, FlightInfo) and hasattr(f, 'explicit_user_confirmation'):
            explicit_confirmation = getattr(f, 'explicit_user_confirmation')
            break

    # If not found in flights, check if a dedicated confirmation flag is passed in payment_id (or other args)
    if explicit_confirmation is None and isinstance(payment_id, str) and payment_id.strip().lower() == 'yes':
        explicit_confirmation = 'yes'

    # Validate explicit confirmation strictly equals 'yes'
    if not (isinstance(explicit_confirmation, str) and explicit_confirmation.strip().lower() == 'yes'):
        raise PolicyViolationException(
            "Explicit user confirmation ('yes') is required before proceeding with reservation updates involving flights, baggage, cabin class, or passenger information."
        )