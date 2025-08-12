from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_cabin_uniformity_requirement import guard_cabin_uniformity_requirement
from airline.i_airline import *
from airline.airline_types import *
from datetime import datetime, timedelta

class TestGuardCabinUniformityRequirement:

    def test_compliance_all_flights_economy(self):
        """
        Policy: "Cabin class must be the same across all flights in a reservation."
        Example: "A user updates a reservation so all flights are reassigned to economy class, ensuring uniform cabin class and complying with the policy."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock(spec=I_Airline)
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=300)],
            created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]

        guard_cabin_uniformity_requirement(history, api, "ZFA04Y", "economy", flights, "credit_card_7815826")

    def test_violation_mixed_cabin_classes(self):
        """
        Policy: "Cabin class must be the same across all flights in a reservation."
        Example: "A reservation is updated with mixed cabin classes, such as economy and business, across different flights within the same reservation. This violates the policy requiring uniform cabin class."
        """
        
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock(spec=I_Airline)
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[ReservationFlight(flight_number="HAT001", date="2024-05-01", price=300, origin="SFO", destination="JFK")],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1990-01-01")],
            payment_history=[Payment(payment_id="credit_card_7815826", amount=300)],
            created_at=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        flights = [FlightInfo(flight_number="HAT001", date="2024-05-01"), FlightInfo(flight_number="HAT002", date="2024-05-02")]

        with pytest.raises(PolicyViolationException):
            guard_cabin_uniformity_requirement(history, api, "ZFA04Y", "economy", flights, "credit_card_7815826")