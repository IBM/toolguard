from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_payment_method_limits_in_booking import guard_payment_method_limits_in_booking
from airline.i_airline import *
from airline.airline_types import *
from datetime import datetime, timedelta

class TestGuardPaymentMethodLimitsInBooking:

    def test_compliance_one_certificate_one_credit_two_gifts(self):
        """
        Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
        Example: "A reservation where the user uses one travel certificate, one credit card, and two gift cards, adhering to the payment method limits."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara@example.com", dob="1990-04-05", payment_methods={"credit_card_1234": CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), "gift_card_5678": GiftCard(source="gift_card", amount=50.0, id="5678"), "certificate_91011": Certificate(source="certificate", id="certificate_91011", amount=100.0)}, saved_passengers=[], membership="gold", reservations=[])

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]
        passengers = [Passenger(first_name="John", last_name="Doe", dob="1985-05-15")]
        payment_methods = [Certificate(source="certificate", id="certificate_91011", amount=100.0), CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), GiftCard(source="gift_card", id="gift_card_5678", amount=50.0)]

        guard_payment_method_limits_in_booking(history, api, "sara_doe_496", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")

    def test_violation_two_certificates_four_gifts(self):
        """
        Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
        Example: "A user attempts to book a reservation using two travel certificates and four gift cards, exceeding the policy limits for each of these payment types."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara@example.com", dob="1990-04-05", payment_methods={"credit_card_1234": CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), "gift_card_5678": GiftCard(source="gift_card", amount=50.0, id="5678"), "certificate_91011": Certificate(source="certificate", id="certificate_91011", amount=100.0)}, saved_passengers=[], membership="gold", reservations=[])

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]
        passengers = [Passenger(first_name="John", last_name="Doe", dob="1985-05-15")]
        payment_methods = [Certificate(source="certificate", id="certificate_91011", amount=100.0), Certificate(source="certificate", id="certificate_91012", amount=100.0), GiftCard(source="gift_card", id="gift_card_5678", amount=50.0), GiftCard(source="gift_card", id="gift_card_5679", amount=50.0), GiftCard(source="gift_card", id="gift_card_5680", amount=50.0), GiftCard(source="gift_card", id="gift_card_5681", amount=50.0)]

        with pytest.raises(PolicyViolationException):
            guard_payment_method_limits_in_booking(history, api, "sara_doe_496", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")

    def test_violation_three_credit_cards(self):
        """
        Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
        Example: "A reservation is attempted using a combination of three credit cards, violating the policy as only one credit card is permitted per reservation."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara@example.com", dob="1990-04-05", payment_methods={"credit_card_1234": CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), "credit_card_5678": CreditCard(source="credit_card", id="credit_card_5678", brand="mastercard", last_four="5678"), "credit_card_91011": CreditCard(source="credit_card", id="credit_card_91011", brand="amex", last_four="9101")}, saved_passengers=[], membership="gold", reservations=[])

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]
        passengers = [Passenger(first_name="John", last_name="Doe", dob="1985-05-15")]
        payment_methods = [CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), CreditCard(source="credit_card", id="credit_card_5678", brand="mastercard", last_four="5678"), CreditCard(source="credit_card", id="credit_card_91011", brand="amex", last_four="9101")]

        with pytest.raises(PolicyViolationException):
            guard_payment_method_limits_in_booking(history, api, "sara_doe_496", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")

    def test_violation_one_certificate_four_gifts(self):
        """
        Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
        Example: "Attempting to book a flight using one travel certificate and four gift cards, which breaches the limit on gift cards."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara@example.com", dob="1990-04-05", payment_methods={"credit_card_1234": CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), "gift_card_5678": GiftCard(source="gift_card", amount=50.0, id="5678"), "certificate_91011": Certificate(source="certificate", id="certificate_91011", amount=100.0)}, saved_passengers=[], membership="gold", reservations=[])

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]
        passengers = [Passenger(first_name="John", last_name="Doe", dob="1985-05-15")]
        payment_methods = [Certificate(source="certificate", id="certificate_91011", amount=100.0), GiftCard(source="gift_card", id="gift_card_5678", amount=50.0), GiftCard(source="gift_card", id="gift_card_5679", amount=50.0), GiftCard(source="gift_card", id="gift_card_5680", amount=50.0), GiftCard(source="gift_card", id="gift_card_5681", amount=50.0)]

        with pytest.raises(PolicyViolationException):
            guard_payment_method_limits_in_booking(history, api, "sara_doe_496", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")

    def test_violation_two_credit_cards(self):
        """
        Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
        Example: "A user uses two credit cards, exceeding the number allowed per reservation."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara@example.com", dob="1990-04-05", payment_methods={"credit_card_1234": CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), "credit_card_5678": CreditCard(source="credit_card", id="credit_card_5678", brand="mastercard", last_four="5678")}, saved_passengers=[], membership="gold", reservations=[])

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]
        passengers = [Passenger(first_name="John", last_name="Doe", dob="1985-05-15")]
        payment_methods = [CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), CreditCard(source="credit_card", id="credit_card_5678", brand="mastercard", last_four="5678")]

        with pytest.raises(PolicyViolationException):
            guard_payment_method_limits_in_booking(history, api, "sara_doe_496", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")

    def test_violation_zero_certificates_three_credit_cards_four_gifts(self):
        """
        Policy: "Each reservation can use at most one travel certificate, one credit card, and three gift cards."
        Example: "An attempt is made to book a reservation using zero travel certificates, three credit cards, and four gift cards, violating the restriction on both credit card and gift card quantities."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara@example.com", dob="1990-04-05", payment_methods={"credit_card_1234": CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), "credit_card_5678": CreditCard(source="credit_card", id="credit_card_5678", brand="mastercard", last_four="5678"), "credit_card_91011": CreditCard(source="credit_card", id="credit_card_91011", brand="amex", last_four="9101"), "gift_card_5678": GiftCard(source="gift_card", amount=50.0, id="5678"), "gift_card_5679": GiftCard(source="gift_card", amount=50.0, id="5679"), "gift_card_5680": GiftCard(source="gift_card", amount=50.0, id="5680"), "gift_card_5681": GiftCard(source="gift_card", amount=50.0, id="5681")}, saved_passengers=[], membership="gold", reservations=[])

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]
        passengers = [Passenger(first_name="John", last_name="Doe", dob="1985-05-15")]
        payment_methods = [CreditCard(source="credit_card", id="credit_card_1234", brand="visa", last_four="1234"), CreditCard(source="credit_card", id="credit_card_5678", brand="mastercard", last_four="5678"), CreditCard(source="credit_card", id="credit_card_91011", brand="amex", last_four="9101"), GiftCard(source="gift_card", id="gift_card_5678", amount=50.0), GiftCard(source="gift_card", id="gift_card_5679", amount=50.0), GiftCard(source="gift_card", id="gift_card_5680", amount=50.0), GiftCard(source="gift_card", id="gift_card_5681", amount=50.0)]

        with pytest.raises(PolicyViolationException):
            guard_payment_method_limits_in_booking(history, api, "sara_doe_496", "SFO", "JFK", "round_trip", "economy", flights, passengers, payment_methods, 2, 1, "yes")
