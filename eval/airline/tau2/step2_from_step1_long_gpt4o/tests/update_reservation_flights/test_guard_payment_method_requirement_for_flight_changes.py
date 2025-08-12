from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_payment_method_requirement_for_flight_changes import guard_payment_method_requirement_for_flight_changes
from airline.i_airline import *
from airline.airline_types import *
from datetime import datetime, timedelta

class TestGuardPaymentMethodRequirementForFlightChanges:

    def test_valid_credit_card_for_flight_change(self):
        """
        Policy: "Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method."
        Example: "The user requests a flight change and provides a valid credit card from their profile, satisfying the policy requirement for payment method."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        user = User(
            user_id="user_123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={
                "credit_card_123": CreditCard(source="credit_card", id="credit_card_123", brand="visa", last_four="1234")
            },
            saved_passengers=[],
            membership="regular",
            reservations=["ZFA04Y"]
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user_123" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        # Invoke function under test
        guard_payment_method_requirement_for_flight_changes(
            history=history,
            api=api,
            reservation_id="ZFA04Y",
            cabin="economy",
            flights=flights,
            payment_id="credit_card_123"
        )

    def test_no_payment_method_provided(self):
        """
        Policy: "Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method."
        Example: "A user attempts to change flights in a reservation without providing any valid payment information such as a gift card or credit card linked to their profile, which contravenes the policy."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        user = User(
            user_id="user_123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={},
            saved_passengers=[],
            membership="regular",
            reservations=["ZFA04Y"]
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user_123" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_payment_method_requirement_for_flight_changes(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                cabin="economy",
                flights=flights,
                payment_id=""
            )

    def test_certificate_as_payment_method(self):
        """
        Policy: "Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method."
        Example: "A flight update process begins with the user providing only a certificate as payment, despite the requirement for a gift card or credit card."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        user = User(
            user_id="user_123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={
                "certificate_123": Certificate(source="certificate", id="certificate_123", amount=100.0)
            },
            saved_passengers=[],
            membership="regular",
            reservations=["ZFA04Y"]
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user_123" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_payment_method_requirement_for_flight_changes(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                cabin="economy",
                flights=flights,
                payment_id="certificate_123"
            )

    def test_payment_method_not_linked_to_profile(self):
        """
        Policy: "Whenever flights in a reservation are changed, ensure the user provides one valid gift card or credit card from their profile as the payment or refund method."
        Example: "A user insists on using a payment method not linked to their profile, such as a friend's credit card, defying the policy's requirement for payment methods to be from the user's profile."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        user = User(
            user_id="user_123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={
                "credit_card_123": CreditCard(source="credit_card", id="credit_card_123", brand="visa", last_four="1234")
            },
            saved_passengers=[],
            membership="regular",
            reservations=["ZFA04Y"]
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user_123" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_payment_method_requirement_for_flight_changes(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                cabin="economy",
                flights=flights,
                payment_id="friend_credit_card_456"
            )
