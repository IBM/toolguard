from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_baggages.guard_baggage_addition_policy import guard_baggage_addition_policy
from airline.airline_types import *
from airline.i_airline import *

def test_increase_bags_gold_business():
    """
    Policy: "When using the update_reservation_baggages tool, you can add checked bags to an existing reservation but cannot remove them..."
    Example: "Increasing checked bags from 2 to 4 on reservation 'ZFA04Y': A gold member in business class adds 2 additional nonfree bags using a stored credit card, correctly applying fees according to policy."
    """
    user = User(
        user_id="user123",
        name=Name(first_name="John", last_name="Doe"),
        address=Address(address1="123 St", address2=None, city="City", country="Country", state="State", zip="12345"),
        email="john@example.com",
        dob="1980-01-01",
        payment_methods={
            "credit_card_7815826": CreditCard(source="credit_card", brand="visa", last_four="1234", id="credit_card_7815826")
        },
        saved_passengers=[],
        membership="gold",
        reservations=["ZFA04Y"]
    )
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="business",
        flights=[],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=2,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None

    guard_baggage_addition_policy(api, reservation_id="ZFA04Y", total_baggages=4, nonfree_baggages=2, payment_id="credit_card_7815826")

def test_cannot_remove_checked_bags():
    """
    Policy: "Change baggage and insurance: The user can add but not remove checked bags."
    Example: "Updating reservation with ID 'ZFA04Y' to reduce the total checked bags from 3 to 2, violating the policy that prevents removing checked bags."
    """
    user = User(
        user_id="user123",
        name=Name(first_name="Jane", last_name="Smith"),
        address=Address(address1="456 Ave", address2=None, city="City", country="Country", state="State", zip="67890"),
        email="jane@example.com",
        dob="1990-02-02",
        payment_methods={
            "credit_card_1111": CreditCard(source="credit_card", brand="mastercard", last_four="1111", id="credit_card_1111")
        },
        saved_passengers=[],
        membership="silver",
        reservations=["ZFA04Y"]
    )
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="LAX",
        destination="ORD",
        flight_type="one_way",
        cabin="economy",
        flights=[],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=3,
        nonfree_baggages=1,
        insurance="yes",
        status=None
    )
    api = MagicMock(spec=I_Airline)
    api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None

    with pytest.raises(PolicyViolationException):
        guard_baggage_addition_policy(api, reservation_id="ZFA04Y", total_baggages=2, nonfree_baggages=1, payment_id="credit_card_1111")