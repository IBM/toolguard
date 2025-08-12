from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_baggages.guard_baggage_addition_policy import guard_baggage_addition_policy
from airline.i_airline import *
from datetime import datetime, timedelta

class TestGuardBaggageAdditionPolicy:

    def test_increasing_checked_bags_for_gold_member_business_class(self):
        """
        Policy: "Increasing checked bags from 2 to 4 on reservation 'ZFA04Y': A gold member in business class adds 2 additional nonfree bags using a stored credit card, correctly applying fees according to policy."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="gold_user_123", name=Name(first_name="John", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"), email="john.doe@example.com", dob="1980-01-01", saved_passengers=[], membership="gold", payment_methods={"credit_card_7815826": CreditCard(source="credit_card", id="credit_card_7815826", brand="visa", last_four="1234")}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="gold_user_123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="business", flights=[], passengers=[], payment_history=[], created_at="2023-01-01T00:00:00", total_baggages=2, nonfree_baggages=0, insurance="no", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "gold_user_123" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.calculate.side_effect = lambda expression: "100" if expression == "2 * 50" else "0"

        guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=4, nonfree_baggages=2, payment_id="credit_card_7815826")

    def test_attempt_to_remove_checked_bags(self):
        """
        Policy: "Updating reservation with ID 'ZFA04Y' to reduce the total checked bags from 3 to 2, violating the policy that prevents removing checked bags."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="regular_user_456", name=Name(first_name="Jane", last_name="Smith"), address=Address(address1="456 Elm St", address2=None, city="Othertown", country="USA", state="NY", zip="67890"), email="jane.smith@example.com", dob="1990-02-02", saved_passengers=[], membership="regular", payment_methods={"credit_card_123456": CreditCard(source="credit_card", id="credit_card_123456", brand="mastercard", last_four="5678")}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="regular_user_456", origin="LAX", destination="ORD", flight_type="one_way", cabin="economy", flights=[], passengers=[], payment_history=[], created_at="2023-02-02T00:00:00", total_baggages=3, nonfree_baggages=1, insurance="yes", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "regular_user_456" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=2, nonfree_baggages=1, payment_id="credit_card_123456")

    def test_using_new_payment_method_not_stored(self):
        """
        Policy: "Attempting to use a new payment method not stored in user profile for baggage fees when updating reservation 'ZFA04Y', violating the policy requiring existing payment methods."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="silver_user_789", name=Name(first_name="Alice", last_name="Johnson"), address=Address(address1="789 Pine St", address2=None, city="Newcity", country="USA", state="TX", zip="54321"), email="alice.johnson@example.com", dob="1985-03-03", saved_passengers=[], membership="silver", payment_methods={"gift_card_987654": GiftCard(source="gift_card", id="gift_card_987654", amount=100)}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="silver_user_789", origin="MIA", destination="ATL", flight_type="round_trip", cabin="economy", flights=[], passengers=[], payment_history=[], created_at="2023-03-03T00:00:00", total_baggages=2, nonfree_baggages=1, insurance="no", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "silver_user_789" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=3, nonfree_baggages=2, payment_id="debit_card_123456")

    def test_incorrect_nonfree_baggages_for_regular_member_basic_economy(self):
        """
        Policy: "Setting total_baggages to 4 but nonfree_baggages to 1 for a regular member in basic economy, violating the policy as regular members get 0 free checked bags in basic economy, so nonfree_baggages should match total_baggages."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="regular_user_456", name=Name(first_name="Jane", last_name="Smith"), address=Address(address1="456 Elm St", address2=None, city="Othertown", country="USA", state="NY", zip="67890"), email="jane.smith@example.com", dob="1990-02-02", saved_passengers=[], membership="regular", payment_methods={"credit_card_123456": CreditCard(source="credit_card", id="credit_card_123456", brand="mastercard", last_four="5678")}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="regular_user_456", origin="LAX", destination="ORD", flight_type="one_way", cabin="basic_economy", flights=[], passengers=[], payment_history=[], created_at="2023-02-02T00:00:00", total_baggages=3, nonfree_baggages=3, insurance="yes", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "regular_user_456" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=4, nonfree_baggages=1, payment_id="credit_card_123456")

    def test_incorrect_nonfree_baggages_for_silver_member_business_class(self):
        """
        Policy: "For a silver member in business class, updating the baggage on reservation 'ZFA04Y' with total_baggages set to 5 checked bags but incorrectly setting nonfree_baggages to 1. The policy grants 3 free checked bags; thus, 2 should be non-free."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="silver_user_789", name=Name(first_name="Alice", last_name="Johnson"), address=Address(address1="789 Pine St", address2=None, city="Newcity", country="USA", state="TX", zip="54321"), email="alice.johnson@example.com", dob="1985-03-03", saved_passengers=[], membership="silver", payment_methods={"certificate_123456": Certificate(source="certificate", id="certificate_123456", amount=200)}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="silver_user_789", origin="MIA", destination="ATL", flight_type="round_trip", cabin="business", flights=[], passengers=[], payment_history=[], created_at="2023-03-03T00:00:00", total_baggages=3, nonfree_baggages=0, insurance="no", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "silver_user_789" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=5, nonfree_baggages=1, payment_id="certificate_123456")

    def test_missing_fee_calculation_for_additional_bags(self):
        """
        Policy: "Adding 3 checked bags to reservation 'ZFA04Y' without calculating and applying a fee for each additional nonfree bag, violating the baggage policy."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="gold_user_123", name=Name(first_name="John", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"), email="john.doe@example.com", dob="1980-01-01", saved_passengers=[], membership="gold", payment_methods={"gift_card_987654": GiftCard(source="gift_card", id="gift_card_987654", amount=100)}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="gold_user_123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[], passengers=[], payment_history=[], created_at="2023-01-01T00:00:00", total_baggages=2, nonfree_baggages=0, insurance="no", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "gold_user_123" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=5, nonfree_baggages=3, payment_id="gift_card_987654")

    def test_incorrect_nonfree_baggages_for_gold_member_economy_class(self):
        """
        Policy: "Updating reservation ID 'ZFA04Y' by setting total_baggages to 6 while nonfree_baggages are only set to 2 for a gold member in economy class, violating the policy as a gold member in economy has 3 free checked bags, meaning nonfree_baggages should be 3."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="gold_user_123", name=Name(first_name="John", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"), email="john.doe@example.com", dob="1980-01-01", saved_passengers=[], membership="gold", payment_methods={"credit_card_7815826": CreditCard(source="credit_card", id="credit_card_7815826", brand="visa", last_four="1234")}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="gold_user_123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="economy", flights=[], passengers=[], payment_history=[], created_at="2023-01-01T00:00:00", total_baggages=3, nonfree_baggages=0, insurance="no", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "gold_user_123" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=6, nonfree_baggages=2, payment_id="credit_card_7815826")

    def test_incorrect_nonfree_baggages_for_regular_member_economy_class(self):
        """
        Policy: "A regular member in economy class updates reservation 'ZFA04Y' by setting total_baggages to 3 and nonfree_baggages to 1, violating the policy because regular members in economy receive 1 free bag and thus nonfree_baggages should be 2."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="regular_user_456", name=Name(first_name="Jane", last_name="Smith"), address=Address(address1="456 Elm St", address2=None, city="Othertown", country="USA", state="NY", zip="67890"), email="jane.smith@example.com", dob="1990-02-02", saved_passengers=[], membership="regular", payment_methods={"credit_card_123456": CreditCard(source="credit_card", id="credit_card_123456", brand="mastercard", last_four="5678")}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="regular_user_456", origin="LAX", destination="ORD", flight_type="one_way", cabin="economy", flights=[], passengers=[], payment_history=[], created_at="2023-02-02T00:00:00", total_baggages=2, nonfree_baggages=1, insurance="yes", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "regular_user_456" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=3, nonfree_baggages=1, payment_id="credit_card_123456")

    def test_using_payment_method_not_stored_in_profile(self):
        """
        Policy: "An attempt to update reservation 'ZFA04Y' using a payment method labeled as 'debit_card_123456', not stored in the user's profile, violating the policy requirement for existing payment methods."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="silver_user_789", name=Name(first_name="Alice", last_name="Johnson"), address=Address(address1="789 Pine St", address2=None, city="Newcity", country="USA", state="TX", zip="54321"), email="alice.johnson@example.com", dob="1985-03-03", saved_passengers=[], membership="silver", payment_methods={"gift_card_987654": GiftCard(source="gift_card", id="gift_card_987654", amount=100)}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="silver_user_789", origin="MIA", destination="ATL", flight_type="round_trip", cabin="economy", flights=[], passengers=[], payment_history=[], created_at="2023-03-03T00:00:00", total_baggages=2, nonfree_baggages=1, insurance="no", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "silver_user_789" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=3, nonfree_baggages=2, payment_id="debit_card_123456")

    def test_incorrect_nonfree_baggages_for_gold_member_basic_economy(self):
        """
        Policy: "For reservation 'ZFA04Y', a gold member in basic economy attempts to set total_baggages at 3 and nonfree_baggages at 0, violating the policy that requires nonfree_baggages to be 1 as gold members receive 2 free bags."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="gold_user_123", name=Name(first_name="John", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="Anytown", country="USA", state="CA", zip="12345"), email="john.doe@example.com", dob="1980-01-01", saved_passengers=[], membership="gold", payment_methods={"credit_card_7815826": CreditCard(source="credit_card", id="credit_card_7815826", brand="visa", last_four="1234")}, reservations=["ZFA04Y"])
        reservation = Reservation(reservation_id="ZFA04Y", user_id="gold_user_123", origin="SFO", destination="JFK", flight_type="round_trip", cabin="basic_economy", flights=[], passengers=[], payment_history=[], created_at="2023-01-01T00:00:00", total_baggages=2, nonfree_baggages=2, insurance="no", status=None)

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "gold_user_123" else None
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        with pytest.raises(PolicyViolationException):
            guard_baggage_addition_policy(history, api, reservation_id="ZFA04Y", total_baggages=3, nonfree_baggages=0, payment_id="credit_card_7815826")
