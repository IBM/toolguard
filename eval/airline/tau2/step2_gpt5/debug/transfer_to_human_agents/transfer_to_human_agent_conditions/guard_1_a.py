from typing import *

import airline
from rt_toolguard.data_types import PolicyViolationException
from airline.airline_types import *
from airline.i_airline import I_Airline

def guard_transfer_to_human_agent_conditions(api: I_Airline, summary: str):
    """
    Policy to check: Transfer a user to a human agent only if the user explicitly requests this transfer
    or if the problem cannot be resolved using available tools and policies within the scope of your actions.
    Include a summary of the user's issue when making the transfer.

    Args:
        api (I_Airline): api to access other tools.
        summary: A summary of the user's issue.
    """
    if not summary or not summary.strip():
        raise PolicyViolationException("Summary of the user's issue must be provided.")

    # Normalize summary for keyword checks
    normalized_summary = summary.lower()

    # Check if the user explicitly requests a human agent
    explicit_request_keywords = [
        "human agent", "real person", "speak with", "talk to", "transfer me", "agent assistance"
    ]
    if any(keyword in normalized_summary for keyword in explicit_request_keywords):
        return  # Allowed due to explicit request

    # If not explicitly requested, check if the issue can be resolved with available tools
    # We will check for keywords that match the capabilities of dependent tools
    tool_keywords = {
        'get_reservation_details': ["reservation details", "reservation id"],
        'update_reservation_flights': ["change flight", "update flight", "flight date change"],
        'calculate': ["calculate", "calculation", "math", "expression"],
        'list_all_airports': ["list of airports", "airport list"],
        'get_flight_status': ["flight status", "status of flight"],
        'search_direct_flight': ["search direct flight", "find direct flight"]
    }

    for tool, keywords in tool_keywords.items():
        if any(keyword in normalized_summary for keyword in keywords):
            # This means the issue can be resolved with an available tool
            raise PolicyViolationException(
                f"The issue described can be resolved using the available tool '{tool}', transfer not allowed."
            )

    # If no explicit request and no matching tool found, allow transfer
    return