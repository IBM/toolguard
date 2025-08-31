from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_flight_segment_transfer_condition(api: I_Airline, summary: str):
    """
    Policy to check: If a user requests to cancel a trip and any segments have already been flown,
    transfer the user to a human agent as the current tool cannot process partial trip cancellations.

    Args:
        api (I_Airline): API to access other tools.
        summary: A summary of the user's issue.
    """
    # We will parse the summary to detect if the user is requesting a cancellation.
    # If so, we will check the reservation's flight segments to see if any have been flown.
    # If any segment is 'flying' or 'landed', we must raise a PolicyViolationException.

    # Simple heuristic: look for keywords indicating cancellation request
    cancel_keywords = ["cancel", "cancellation", "terminate", "end trip", "stop trip"]
    if any(keyword in summary.lower() for keyword in cancel_keywords):
        # Extract reservation IDs from the summary (assuming they are mentioned)
        # In a real implementation, the reservation ID would be passed explicitly.
        # Here, we will assume the summary contains a reservation ID in a known format (e.g., 6-char alphanumeric)
        import re
        reservation_ids = re.findall(r'\b[A-Z0-9]{6}\b', summary)
        for res_id in reservation_ids:
            try:
                reservation = api.get_reservation_details(res_id)
            except ValueError:
                continue  # If reservation not found, skip
            for flight in reservation.flights:
                status = api.get_flight_status(flight.flight_number, flight.date)
                if status in ('flying', 'landed'):
                    raise PolicyViolationException(
                        "One or more segments have already been flown. Transfer to a human agent is required."
                    )
    # If no cancellation request or no flown segments, pass without violation