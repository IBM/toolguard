from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_flight_modification_api_limitation_check import guard_flight_modification_api_limitation_check
from airline.i_airline import *
from airline.airline_types import *
from datetime import datetime, timedelta

class TestGuardFlightModificationApiLimitationCheck:

    def test_update_reservation_preserving_structure(self):
        """
        Policy: "Agents must verify the following before using the Flight Modification API: Basic economy flights are unmodifiable. For other flight reservations, ensure that origin, destination, and trip type remain unchanged from the initial booking. Prices for flight segments retained stay at original rates, not updated by the API. Manual validation of segment prices is required."
        Example: "Update reservation flights with the same 'origin' and 'destination', ensuring no changes in basic structure, and manually verify segment prices, complying with the policy."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="business",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=500, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=500)],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None
        api.get_scheduled_flight.side_effect = lambda flight_number: Flight(
            flight_number="HAT001",
            origin="SFO",
            destination="JFK",
            scheduled_departure_time_est="06:00:00",
            scheduled_arrival_time_est="07:00:00",
            dates={"2024-05-01": FlightDateStatusAvailable(
                status="available",
                available_seats={"business": 10, "economy": 20, "basic_economy": 30},
                prices={"business": 500, "economy": 300, "basic_economy": 200}
            )}
        ) if flight_number == "HAT001" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        guard_flight_modification_api_limitation_check(history, api, "ZFA04Y", "business", flights, "credit_card_7815826")

    def test_change_cabin_class_basic_economy(self):
        """
        Policy: "Agents must verify the following before using the Flight Modification API: Basic economy flights are unmodifiable."
        Example: "An agent attempts to use the Flight Modification API to change the cabin class of a reservation booked under 'basic_economy'. This violates the policy since 'basic_economy' flights are unmodifiable."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="basic_economy",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=200, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=200)],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        with pytest.raises(PolicyViolationException):
            guard_flight_modification_api_limitation_check(history, api, "ZFA04Y", "economy", flights, "credit_card_7815826")

    def test_change_origin(self):
        """
        Policy: "Agents must verify the following before using the Flight Modification API: For other flight reservations, ensure that origin, destination, and trip type remain unchanged from the initial booking."
        Example: "The agent changes the origin from 'SFO' to 'LAX' in a reservation update, violating the policy as the origin must remain unchanged."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="business",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=500, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=500)],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        with pytest.raises(PolicyViolationException):
            guard_flight_modification_api_limitation_check(history, api, "ZFA04Y", "business", flights, "credit_card_7815826")

    def test_change_destination(self):
        """
        Policy: "Agents must verify the following before using the Flight Modification API: For other flight reservations, ensure that origin, destination, and trip type remain unchanged from the initial booking."
        Example: "Changing the destination from 'JFK' to 'BOS' during a reservation update violates the policy because the destination must remain unchanged."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="business",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=500, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=500)],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        with pytest.raises(PolicyViolationException):
            guard_flight_modification_api_limitation_check(history, api, "ZFA04Y", "business", flights, "credit_card_7815826")

    def test_change_trip_type(self):
        """
        Policy: "Agents must verify the following before using the Flight Modification API: For other flight reservations, ensure that origin, destination, and trip type remain unchanged from the initial booking."
        Example: "An agent updates a flight reservation from a 'round_trip' to a 'one_way' trip, violating the policy since the trip type cannot be altered."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="business",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=500, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=500)],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        with pytest.raises(PolicyViolationException):
            guard_flight_modification_api_limitation_check(history, api, "ZFA04Y", "business", flights, "credit_card_7815826")

    def test_manual_price_verification_required(self):
        """
        Policy: "Agents must verify the following before using the Flight Modification API: Prices for flight segments retained stay at original rates, not updated by the API. Manual validation of segment prices is required."
        Example: "An agent uses the API to modify a flight reservation without manually verifying the prices of retained flight segments, violating the policy that requires agents to confirm original rates manually."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="business",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=500, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=500)],
            created_at=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        with pytest.raises(PolicyViolationException):
            guard_flight_modification_api_limitation_check(history, api, "ZFA04Y", "business", flights, "credit_card_7815826")
