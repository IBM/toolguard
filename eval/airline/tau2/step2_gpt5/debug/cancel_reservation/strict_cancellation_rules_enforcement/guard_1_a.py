from typing import *
from datetime import datetime, timedelta

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_strict_cancellation_rules_enforcement(api: I_Airline, reservation_id: str):
    """
    Enforces strict cancellation rules before allowing 'cancel_reservation'.
    Conditions for cancellation:
      - Reservation cancelled by the airline.
      - Within 24 hours of booking.
      - Travel insurance applies due to health or weather.
      - Business flights can always be cancelled if unused.
    Partial cancellations are prohibited.
    """
    # Get reservation details
    reservation = api.get_reservation_details(reservation_id)

    # Check if reservation already cancelled
    if reservation.status == 'cancelled':
        raise PolicyViolationException("Reservation is already cancelled.")

    # Ensure no flight segments have been flown
    for flight in reservation.flights:
        flight_status = api.get_flight_instance(flight.flight_number, flight.date)
        if getattr(flight_status, 'status', None) in ['landed', 'flying']:
            raise PolicyViolationException("Partial cancellations are prohibited; some segments already flown.")

    # Check if any flight was cancelled by the airline
    airline_cancelled = any(getattr(api.get_flight_instance(f.flight_number, f.date), 'status', None) == 'cancelled' for f in reservation.flights)

    # Check if within 24 hours of booking
    booking_time = datetime.strptime(reservation.created_at, "%Y-%m-%dT%H:%M:%S")
    within_24_hours = datetime.now() - booking_time <= timedelta(hours=24)

    # Check travel insurance
    has_insurance = reservation.insurance == 'yes'

    # Determine if cancellation is allowed
    if airline_cancelled or within_24_hours:
        return
    if reservation.cabin == 'business':
        return
    if has_insurance:
        return

    # If none of the conditions met, raise violation
    raise PolicyViolationException("Cancellation not allowed per strict policy rules.")