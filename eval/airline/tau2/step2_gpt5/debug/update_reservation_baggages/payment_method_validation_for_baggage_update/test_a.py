from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_baggages.guard_payment_method_validation_for_baggage_update import guard_payment_method_validation_for_baggage_update
from airline.airline_types import *
from airline.i_airline import *

class TestGuardPaymentMethodValidationForBaggageUpdate:

    def test_credit_card_stored_in_profile(self):
        """ 
        Policy: Ensure the payment method used is stored in the user's profile before using the 'update_reservation_baggages' tool.
        Example: A user successfully updates their reservation baggages using a credit card stored in their profile, ensuring secure payment.
        """
        user = User(
            user_id="user123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="New York", country="USA", state="NY", zip="10001"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={
                "credit_card_7815826": CreditCard(source="credit_card", id="credit_card_7815826", brand="visa", last_four="1234")
            },
            saved_passengers=[],
            membership="gold",
            reservations=["resv001"]
        )
        reservation = Reservation(
            reservation_id="resv001",
            user_id="user123",
            origin="JFK",
            destination="LAX",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[],
            payment_history=[],
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=1,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv001" else None

        # Should not raise exception
        guard_payment_method_validation_for_baggage_update(api, reservation_id="resv001", total_baggages=2, nonfree_baggages=1, payment_id="credit_card_7815826")

    def test_certificate_not_in_profile_raises(self):
        """ 
        Policy: Ensure the payment method used is stored in the user's profile before using the 'update_reservation_baggages' tool.
        Example: A user attempts to update their reservation baggages using a certificate or credit card that is not stored in their profile, which leads to transaction insecurity.
        """
        user = User(
            user_id="user123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="New York", country="USA", state="NY", zip="10001"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods={},
            saved_passengers=[],
            membership="gold",
            reservations=["resv001"]
        )
        reservation = Reservation(
            reservation_id="resv001",
            user_id="user123",
            origin="JFK",
            destination="LAX",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[],
            payment_history=[],
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=1,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv001" else None

        with pytest.raises(PolicyViolationException):
            guard_payment_method_validation_for_baggage_update(api, reservation_id="resv001", total_baggages=2, nonfree_baggages=1, payment_id="certificate_999999")

    def test_multiple_gift_cards_exceeding_limit(self):
        """ 
        Policy: Payment: each reservation can use at most one travel certificate, at most one credit card, and at most three gift cards.
        Example: A user tries to update their reservation baggages using multiple gift cards, exceeding the allowed limit and thus violating payment method constraints.
        """
        gift_cards = {
            f"gift_card_{i}": GiftCard(source="gift_card", id=f"gift_card_{i}", amount=100.0) for i in range(4)
        }
        user = User(
            user_id="user123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="New York", country="USA", state="NY", zip="10001"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods=gift_cards,
            saved_passengers=[],
            membership="gold",
            reservations=["resv001"]
        )
        reservation = Reservation(
            reservation_id="resv001",
            user_id="user123",
            origin="JFK",
            destination="LAX",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[],
            payment_history=[],
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=1,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv001" else None

        with pytest.raises(PolicyViolationException):
            guard_payment_method_validation_for_baggage_update(api, reservation_id="resv001", total_baggages=2, nonfree_baggages=1, payment_id="gift_card_0")

    def test_multiple_certificates_exceeding_limit(self):
        """ 
        Policy: Payment: each reservation can use at most one travel certificate.
        Example: A user attempts to use a combination of certificates for paying the baggage update, exceeding the allowed limit per reservation.
        """
        certificates = {
            f"certificate_{i}": Certificate(source="certificate", id=f"certificate_{i}", amount=200.0) for i in range(2)
        }
        user = User(
            user_id="user123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 Main St", address2=None, city="New York", country="USA", state="NY", zip="10001"),
            email="john.doe@example.com",
            dob="1990-01-01",
            payment_methods=certificates,
            saved_passengers=[],
            membership="gold",
            reservations=["resv001"]
        )
        reservation = Reservation(
            reservation_id="resv001",
            user_id="user123",
            origin="JFK",
            destination="LAX",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[],
            payment_history=[],
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=1,
            nonfree_baggages=0,
            insurance="no",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv001" else None

        with pytest.raises(PolicyViolationException):
            guard_payment_method_validation_for_baggage_update(api, reservation_id="resv001", total_baggages=2, nonfree_baggages=1, payment_id="certificate_0")