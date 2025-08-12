from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_baggages.guard_payment_method_validation_for_baggage_update import guard_payment_method_validation_for_baggage_update
from airline.i_airline import *
from datetime import datetime, timedelta

class TestGuardPaymentMethodValidationForBaggageUpdate:

    def test_successful_update_with_stored_credit_card(self):
        """
        Policy: "Ensure the payment method used is stored in the user's profile before using the 'update_reservation_baggages' tool."
        Example: "A user successfully updates their reservation baggages using a credit card stored in their profile, ensuring secure payment."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(
            user_id="user_123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={
                "credit_card_7815826": CreditCard(source="credit_card", id="credit_card_7815826", brand="visa", last_four="1234")
            },
            saved_passengers=[],
            membership="regular",
            reservations=["ZFA04Y"]
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user_123" else None

        guard_payment_method_validation_for_baggage_update(
            history=history,
            api=api,
            reservation_id="ZFA04Y",
            total_baggages=2,
            nonfree_baggages=1,
            payment_id="credit_card_7815826"
        )

    def test_violation_with_unstored_certificate(self):
        """
        Policy: "Ensure the payment method used is stored in the user's profile before using the 'update_reservation_baggages' tool."
        Example: "A user attempts to update their reservation baggages using a certificate or credit card that is not stored in their profile, which leads to transaction insecurity."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

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

        with pytest.raises(PolicyViolationException):
            guard_payment_method_validation_for_baggage_update(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                total_baggages=2,
                nonfree_baggages=1,
                payment_id="certificate_7815826"
            )

    def test_violation_with_exceeding_gift_card_limit(self):
        """
        Policy: "Ensure the payment method used is stored in the user's profile before using the 'update_reservation_baggages' tool."
        Example: "A user tries to update their reservation baggages using multiple gift cards, exceeding the allowed limit and thus violating payment method constraints."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(
            user_id="user_123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={
                "gift_card_7815826": GiftCard(source="gift_card", id="gift_card_7815826", amount=50.0),
                "gift_card_7815827": GiftCard(source="gift_card", id="gift_card_7815827", amount=50.0),
                "gift_card_7815828": GiftCard(source="gift_card", id="gift_card_7815828", amount=50.0),
                "gift_card_7815829": GiftCard(source="gift_card", id="gift_card_7815829", amount=50.0)
            },
            saved_passengers=[],
            membership="regular",
            reservations=["ZFA04Y"]
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user_123" else None

        with pytest.raises(PolicyViolationException):
            guard_payment_method_validation_for_baggage_update(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                total_baggages=2,
                nonfree_baggages=1,
                payment_id="gift_card_7815826"
            )

    def test_violation_with_exceeding_certificate_limit(self):
        """
        Policy: "Ensure the payment method used is stored in the user's profile before using the 'update_reservation_baggages' tool."
        Example: "A user attempts to use a combination of certificates for paying the baggage update, exceeding the allowed limit per reservation."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(
            user_id="user_123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={
                "certificate_7815826": Certificate(source="certificate", id="certificate_7815826", amount=100.0),
                "certificate_7815827": Certificate(source="certificate", id="certificate_7815827", amount=100.0)
            },
            saved_passengers=[],
            membership="regular",
            reservations=["ZFA04Y"]
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "user_123" else None

        with pytest.raises(PolicyViolationException):
            guard_payment_method_validation_for_baggage_update(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                total_baggages=2,
                nonfree_baggages=1,
                payment_id="certificate_7815826"
            )
