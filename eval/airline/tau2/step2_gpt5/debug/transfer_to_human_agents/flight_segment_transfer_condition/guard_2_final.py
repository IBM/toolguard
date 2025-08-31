from typing import *
import re

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
    # Keywords that indicate a cancellation request
    cancel_keywords = ["cancel", "cancellation", "terminate", "end trip", "stop trip"]
    summary_lower = summary.lower()

    # Check if the summary indicates a cancellation request
    if any(keyword in summary_lower for keyword in cancel_keywords):
        # Attempt to extract reservation IDs from the summary (6-character alphanumeric)
        reservation_ids = re.findall(r'\b[A-Z0-9]{6}\b', summary)

        for res_id in reservation_ids:
            try:
                reservation = api.get_reservation_details(res_id)
            except ValueError:
                continue  # Skip if reservation not found

            # Check each flight segment's status
            for flight in reservation.flights:
                try:
                    status = api.get_flight_status(flight.flight_number, flight.date)
                except ValueError:
                    continue  # Skip if flight not found

                if status in ('flying', 'landed'):
                    # Violation: partial trip cancellation required, must transfer to human agent
                    raise PolicyViolationException(
                        "One or more segments have already been flown. Transfer to a human agent is required."
                    )

        # If no reservation IDs found in summary, we cannot verify segments — be safe and raise
        if not reservation_ids:
            raise PolicyViolationException(
                "Cancellation request detected but reservation details are missing. Transfer to a human agent is required."
            )

    # If no cancellation request detected, no violation