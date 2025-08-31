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

        # If no reservation IDs found, try to get them from the user's profile
        if not reservation_ids:
            try:
                # Attempt to get user details and extract reservation IDs
                # Since we don't have user_id in args, we cannot fetch user details reliably
                # Therefore, per policy, transfer to human agent
                raise PolicyViolationException(
                    "Cancellation request detected but reservation details are missing. Transfer to a human agent is required."
                )
            except ValueError:
                raise PolicyViolationException(
                    "Cancellation request detected but reservation details are missing. Transfer to a human agent is required."
                )

        # For each reservation, check if any segment has been flown
        for res_id in reservation_ids:
            try:
                reservation = api.get_reservation_details(res_id)
            except ValueError:
                raise PolicyViolationException(
                    f"Reservation {res_id} not found. Transfer to a human agent is required."
                )

            for flight in reservation.flights:
                try:
                    status = api.get_flight_status(flight.flight_number, flight.date)
                except ValueError:
                    raise PolicyViolationException(
                        f"Flight {flight.flight_number} on {flight.date} not found. Transfer to a human agent is required."
                    )

                # If any segment is already flown or in-flight, transfer to human agent
                if status in ('flying', 'landed'):
                    raise PolicyViolationException(
                        "One or more segments have already been flown. Transfer to a human agent is required."
                    )
    return