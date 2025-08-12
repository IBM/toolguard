from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_user_id_requirement_for_flight_booking import guard_user_id_requirement_for_flight_booking
from airline.i_airline import *
from airline.airline_types import *
from datetime import datetime, timedelta

class TestGuardUserIdRequirementForFlightBooking:

    def test_user_id_obtained_before_inquiries(self):
        """
        Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
        Example: "The agent asks the user for their user ID before proceeding with any inquiries on trip type, origin, destination, passenger list, and payment methods, ensuring compliance."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])
        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        # Invoke function under test
        guard_user_id_requirement_for_flight_booking(
            history=history,
            api=api,
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[FlightInfo(flight_number="HAT001", date="2024-05-01")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1985-06-15")],
            payment_methods=[Payment(payment_id="credit_card_1234", amount=500)],
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes"
        )

    def test_proceed_without_user_id(self):
        """
        Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
        Example: "The agent proceeds to book a flight without first obtaining the user ID, starting inquiries directly with the trip type, origin, and destination, which violates the policy of collecting user ID first."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = False

        # Mock the API
        api = MagicMock(spec=I_Airline)

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_user_id_requirement_for_flight_booking(
                history=history,
                api=api,
                user_id="",
                origin="SFO",
                destination="JFK",
                flight_type="round_trip",
                cabin="economy",
                flights=[FlightInfo(flight_number="HAT001", date="2024-05-01")],
                passengers=[Passenger(first_name="John", last_name="Doe", dob="1985-06-15")],
                payment_methods=[Payment(payment_id="credit_card_1234", amount=500)],
                total_baggages=2,
                nonfree_baggages=1,
                insurance="yes"
            )

    def test_inquiries_without_user_id_confirmation(self):
        """
        Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
        Example: "Booking is initiated with discussions about payment methods, flight details, and cabin preferences without confirming the user ID beforehand, contrary to policy requirements."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = False

        # Mock the API
        api = MagicMock(spec=I_Airline)

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_user_id_requirement_for_flight_booking(
                history=history,
                api=api,
                user_id="",
                origin="SFO",
                destination="JFK",
                flight_type="round_trip",
                cabin="economy",
                flights=[FlightInfo(flight_number="HAT001", date="2024-05-01")],
                passengers=[Passenger(first_name="John", last_name="Doe", dob="1985-06-15")],
                payment_methods=[Payment(payment_id="credit_card_1234", amount=500)],
                total_baggages=2,
                nonfree_baggages=1,
                insurance="yes"
            )

    def test_direct_inquiries_without_user_id(self):
        """
        Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
        Example: "The agent asks for insurance preferences, baggage information, and passenger count directly without verifying the user ID at the start, failing to adhere to user ID sequence policy."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = False

        # Mock the API
        api = MagicMock(spec=I_Airline)

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_user_id_requirement_for_flight_booking(
                history=history,
                api=api,
                user_id="",
                origin="SFO",
                destination="JFK",
                flight_type="round_trip",
                cabin="economy",
                flights=[FlightInfo(flight_number="HAT001", date="2024-05-01")],
                passengers=[Passenger(first_name="John", last_name="Doe", dob="1985-06-15")],
                payment_methods=[Payment(payment_id="credit_card_1234", amount=500)],
                total_baggages=2,
                nonfree_baggages=1,
                insurance="yes"
            )
