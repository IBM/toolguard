import unittest
from unittest.mock import MagicMock, patch

# Importing the necessary modules from the application
from my_app.update_reservation_baggages.guard_update_reservation_baggages import guard_update_reservation_baggages
from my_app.common import *
from my_app.domain import *


class TestGuardToolCallWithoutSimultaneousUserInteraction(unittest.TestCase):
    
    # Compliance Test Cases
    def test_update_reservation_baggages_no_other_tool_calls(self):
        """
        The system performs 'update_reservation_baggages' ensuring no other tool calls are active, and retrieves details only after completion.
        """
        args = UpdateReservationBaggagesRequest.model_construct(
            reservation_id='ZFA04Y',
            total_baggages=2,
            nonfree_baggages=1,
            payment_id='credit_card_7815826'
        )

        history = MagicMock()
        history.ask_bool.return_value = False  # Mock that no other tool calls are active

        api = MagicMock()

        # Invoke the function under test
        guard_update_reservation_baggages(args, history, api)

    # Violation Test Cases
    def test_violation_simultaneous_tool_call(self):
        """
        A system attempts to update reservation baggages while simultaneously making a tool call to get flight details using the 'get_flight_details' tool, violating the policy by compromising process integrity.
        """
        args = UpdateReservationBaggagesRequest.model_construct(
            reservation_id='ZFA04Y',
            total_baggages=2,
            nonfree_baggages=1,
            payment_id='credit_card_7815826'
        )

        history = MagicMock()
        history.ask_bool.return_value = True  # Mock that another tool call is active

        api = MagicMock()

        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_baggages(args, history, api)

    def test_violation_simultaneous_user_interaction(self):
        """
        The reservation update using 'update_reservation_baggages' overlaps with communication thanking the user for patience, which violates the policy due to simultaneous user interaction.
        """
        args = UpdateReservationBaggagesRequest.model_construct(
            reservation_id='ZFA04Y',
            total_baggages=2,
            nonfree_baggages=1,
            payment_id='credit_card_7815826'
        )

        history = MagicMock()
        history.ask_bool.return_value = True  # Mock that user interaction is happening

        api = MagicMock()

        with self.assertRaises(PolicyViolationException):
            guard_update_reservation_baggages(args, history, api)


if __name__ == '__main__':
    unittest.main()
