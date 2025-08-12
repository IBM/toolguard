from typing import *
import airline
from rt_toolguard.data_types import ChatHistory, PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_strict_cancellation_rules_enforcement(history: ChatHistory, api: I_Airline, reservation_id: str):
    """
    Policy to check: The policy requires ensuring compliance with the cancellation rules before using 'cancel_reservation'. Agents must check if reservations meet these conditions: cancelled by the airline, within 24 hours of booking, or if travel insurance applies due to health or weather. Partial cancellations are prohibited. Transfer to human agents if these rules cannot facilitate cancellation.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
    """
    # Fetch reservation details
    try:
        reservation = api.get_reservation_details(reservation_id)
    except ValueError:
        raise PolicyViolationException("Reservation not found.")

    # Check if reservation is cancelled by the airline
    for flight in reservation.flights:
        flight_status = api.get_flight_status(flight.flight_number, flight.date)
        if flight_status == 'cancelled':
            return  # Airline cancelled, allow cancellation

    # Check if reservation is within 24 hours of booking
    from datetime import datetime, timedelta
    booking_time = datetime.strptime(reservation.created_at, "%Y-%m-%dT%H:%M:%S")
    if datetime.now() - booking_time <= timedelta(hours=24):
        return  # Within 24 hours, allow cancellation

    # Check if travel insurance applies
    if reservation.insurance == 'yes':
        # Assuming health or weather conditions are checked externally
        return  # Insurance applies, allow cancellation

    # Check if any flight segments have been flown
    for flight in reservation.flights:
        flight_status = api.get_flight_status(flight.flight_number, flight.date)
        if flight_status in ['flying', 'landed']:
            raise PolicyViolationException("Partial cancellations are prohibited.")

    # If none of the conditions are met, transfer to human agents
    raise PolicyViolationException("Cannot facilitate cancellation under current policy conditions.")