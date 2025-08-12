from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_flight_passenger_limit_for_booking import guard_flight_passenger_limit_for_booking
from airline.airline_types import *
from airline.i_airline import I_Airline
from datetime import datetime, timedelta

class TestGuardFlightPassengerLimitForBooking:

    def test_booking_for_three_passengers_compliance(self):
        """
        Policy: "A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin."
        Example: "Booking for three passengers: John Doe, Jane Smith, and Alex Murphy, all flying economy class from JFK to SFO with identical flight segments, fits the maximum passenger limit and same flight itinerary requirement."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock(spec=I_Airline)
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flight_info = FlightInfo(flight_number="HAT001", date="2024-05-01")
        api.get_flight_instance.side_effect = lambda flight_number, date: FlightDateStatusAvailable(status="available", available_seats={"economy": 100}, prices={"economy": 200}) if flight_number == "HAT001" and date == "2024-05-01" else None

        passengers = [Passenger(first_name="John", last_name="Doe", dob="1980-01-01"), Passenger(first_name="Jane", last_name="Smith", dob="1985-02-02"), Passenger(first_name="Alex", last_name="Murphy", dob="1990-03-03")]

        guard_flight_passenger_limit_for_booking(history, api, "sara_doe_496", "JFK", "SFO", "one_way", "economy", [flight_info], passengers, [], 0, 0, "no")

    def test_reservation_attempted_for_six_passengers_violation(self):
        """
        Policy: "A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin."
        Example: "A reservation is attempted for six passengers: John Doe, Jane Smith, Alex Murphy, Ella Brown, Chris Davis, and Emily White, which exceeds the maximum allowed five passengers per reservation."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock(spec=I_Airline)
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flight_info = FlightInfo(flight_number="HAT001", date="2024-05-01")
        api.get_flight_instance.side_effect = lambda flight_number, date: FlightDateStatusAvailable(status="available", available_seats={"economy": 100}, prices={"economy": 200}) if flight_number == "HAT001" and date == "2024-05-01" else None

        passengers = [Passenger(first_name="John", last_name="Doe", dob="1980-01-01"), Passenger(first_name="Jane", last_name="Smith", dob="1985-02-02"), Passenger(first_name="Alex", last_name="Murphy", dob="1990-03-03"), Passenger(first_name="Ella", last_name="Brown", dob="1995-04-04"), Passenger(first_name="Chris", last_name="Davis", dob="2000-05-05"), Passenger(first_name="Emily", last_name="White", dob="2005-06-06")]

        with pytest.raises(PolicyViolationException):
            guard_flight_passenger_limit_for_booking(history, api, "sara_doe_496", "JFK", "SFO", "one_way", "economy", [flight_info], passengers, [], 0, 0, "no")

    def test_different_cabin_classes_violation(self):
        """
        Policy: "A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin."
        Example: "A reservation is made for four passengers: John Doe, Jane Smith, Alex Murphy, and Ella Brown, with John flying business class and the others flying economy. Cabin classes must be the same for all passengers within a reservation."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock(spec=I_Airline)
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flight_info = FlightInfo(flight_number="HAT001", date="2024-05-01")
        api.get_flight_instance.side_effect = lambda flight_number, date: FlightDateStatusAvailable(status="available", available_seats={"economy": 100, "business": 50}, prices={"economy": 200, "business": 500}) if flight_number == "HAT001" and date == "2024-05-01" else None

        passengers = [Passenger(first_name="John", last_name="Doe", dob="1980-01-01"), Passenger(first_name="Jane", last_name="Smith", dob="1985-02-02"), Passenger(first_name="Alex", last_name="Murphy", dob="1990-03-03"), Passenger(first_name="Ella", last_name="Brown", dob="1995-04-04")]

        with pytest.raises(PolicyViolationException):
            guard_flight_passenger_limit_for_booking(history, api, "sara_doe_496", "JFK", "SFO", "one_way", "business", [flight_info], passengers, [], 0, 0, "no")

    def test_different_flight_itineraries_violation(self):
        """
        Policy: "A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin."
        Example: "Three passengers, John Doe, Jane Smith, and Alex Murphy, have different flight itineraries: John and Jane are flying from JFK to SFO, and Alex is flying from LAX to SFO. All passengers must share the same flight itinerary."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock(spec=I_Airline)
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flight_info_jfk_sfo = FlightInfo(flight_number="HAT001", date="2024-05-01")
        flight_info_lax_sfo = FlightInfo(flight_number="HAT002", date="2024-05-01")
        api.get_flight_instance.side_effect = lambda flight_number, date: FlightDateStatusAvailable(status="available", available_seats={"economy": 100}, prices={"economy": 200}) if flight_number in ["HAT001", "HAT002"] and date == "2024-05-01" else None

        passengers = [Passenger(first_name="John", last_name="Doe", dob="1980-01-01"), Passenger(first_name="Jane", last_name="Smith", dob="1985-02-02"), Passenger(first_name="Alex", last_name="Murphy", dob="1990-03-03")]

        with pytest.raises(PolicyViolationException):
            guard_flight_passenger_limit_for_booking(history, api, "sara_doe_496", "JFK", "SFO", "one_way", "economy", [flight_info_jfk_sfo, flight_info_lax_sfo], passengers, [], 0, 0, "no")

    def test_different_flight_types_violation(self):
        """
        Policy: "A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin."
        Example: "Booking for two passengers, John Doe and Jane Smith, with different flight types: John on a 'one_way' ticket and Jane on a 'round_trip' ticket. Flight types must be identical among passengers in the reservation."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock(spec=I_Airline)
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flight_info = FlightInfo(flight_number="HAT001", date="2024-05-01")
        api.get_flight_instance.side_effect = lambda flight_number, date: FlightDateStatusAvailable(status="available", available_seats={"economy": 100}, prices={"economy": 200}) if flight_number == "HAT001" and date == "2024-05-01" else None

        passengers = [Passenger(first_name="John", last_name="Doe", dob="1980-01-01"), Passenger(first_name="Jane", last_name="Smith", dob="1985-02-02")]

        with pytest.raises(PolicyViolationException):
            guard_flight_passenger_limit_for_booking(history, api, "sara_doe_496", "JFK", "SFO", "round_trip", "economy", [flight_info], passengers, [], 0, 0, "no")

    def test_partial_shared_flight_itinerary_violation(self):
        """
        Policy: "A flight reservation can have at most five passengers, and all must fly the same flights in the same cabin."
        Example: "A reservation for five passengers includes one passenger flying only part of the shared flight itinerary. All passengers are required to fly all shared flights together."
        """
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock(spec=I_Airline)
        user = User(user_id="sara_doe_496", name=Name(first_name="Sara", last_name="Doe"), address=Address(address1="123 Main St", address2=None, city="San Francisco", country="USA", state="CA", zip="94105"), email="sara.doe@example.com", dob="1990-04-05", payment_methods={}, saved_passengers=[], membership="regular", reservations=[])
        api.get_user_details.side_effect = lambda user_id: user if user_id == "sara_doe_496" else None

        flight_info = FlightInfo(flight_number="HAT001", date="2024-05-01")
        api.get_flight_instance.side_effect = lambda flight_number, date: FlightDateStatusAvailable(status="available", available_seats={"economy": 100}, prices={"economy": 200}) if flight_number == "HAT001" and date == "2024-05-01" else None

        passengers = [Passenger(first_name="John", last_name="Doe", dob="1980-01-01"), Passenger(first_name="Jane", last_name="Smith", dob="1985-02-02"), Passenger(first_name="Alex", last_name="Murphy", dob="1990-03-03"), Passenger(first_name="Ella", last_name="Brown", dob="1995-04-04"), Passenger(first_name="Chris", last_name="Davis", dob="2000-05-05")]

        with pytest.raises(PolicyViolationException):
            guard_flight_passenger_limit_for_booking(history, api, "sara_doe_496", "JFK", "SFO", "one_way", "economy", [flight_info], passengers, [], 0, 0, "no")
