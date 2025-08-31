from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.send_certificate.guard_compensation_for_cancelled_or_delayed_flights import guard_compensation_for_cancelled_or_delayed_flights
from airline.airline_types import *
from airline.i_airline import *

class TestGuardCompensationForCancelledOrDelayedFlights:

    def test_silver_member_cancelled_flight_two_passengers(self):
        """ 
        Policy: "If the user is silver/gold member or has travel insurance or flies business, and complains about cancelled flights in a reservation, the agent can offer a certificate as a gesture after confirming the facts, with the amount being $100 times the number of passengers."
        Example: "After a silver member complains about their flight being canceled, the agent verifies membership and sends a certificate of $100 per passenger to the two passengers in the reservation."
        """
        user = User(
            user_id="user123",
            name=Name(first_name="John", last_name="Doe"),
            address=Address(address1="123 St", address2=None, city="City", country="Country", state="State", zip="12345"),
            email="john@example.com",
            dob="1980-01-01",
            payment_methods={},
            saved_passengers=[],
            membership="silver",
            reservations=["resv1"]
        )
        reservation = Reservation(
            reservation_id="resv1",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="one_way",
            cabin="economy",
            flights=[ReservationFlight(flight_number="FL123", origin="SFO", destination="JFK", date="2024-06-01", price=500)],
            passengers=[Passenger(first_name="John", last_name="Doe", dob="1980-01-01"), Passenger(first_name="Jane", last_name="Doe", dob="1985-05-05")],
            payment_history=[],
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=0,
            nonfree_baggages=0,
            insurance="no",
            status="cancelled"
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda uid: user if uid == "user123" else None
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv1" else None
        api.get_flight_status.side_effect = lambda fn, date: "cancelled" if fn == "FL123" and date == "2024-06-01" else "on time"

        guard_compensation_for_cancelled_or_delayed_flights(api, user_id="user123", amount=200)

    def test_regular_member_no_insurance_basic_economy(self):
        """ 
        Policy: "Do not compensate if the user is regular member and has no travel insurance and flies (basic) economy."
        Example: "An agent tries to send a $100 compensation certificate for a canceled flight to a regular member who does not have travel insurance and is traveling in basic economy class, violating the eligibility criteria."
        """
        user = User(
            user_id="user456",
            name=Name(first_name="Alice", last_name="Smith"),
            address=Address(address1="456 St", address2=None, city="City", country="Country", state="State", zip="67890"),
            email="alice@example.com",
            dob="1990-02-02",
            payment_methods={},
            saved_passengers=[],
            membership="regular",
            reservations=["resv2"]
        )
        reservation = Reservation(
            reservation_id="resv2",
            user_id="user456",
            origin="LAX",
            destination="ORD",
            flight_type="one_way",
            cabin="basic_economy",
            flights=[ReservationFlight(flight_number="FL456", origin="LAX", destination="ORD", date="2024-06-02", price=300)],
            passengers=[Passenger(first_name="Alice", last_name="Smith", dob="1990-02-02")],
            payment_history=[],
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_baggages=0,
            nonfree_baggages=0,
            insurance="no",
            status="cancelled"
        )

        api = MagicMock(spec=I_Airline)
        api.get_user_details.side_effect = lambda uid: user if uid == "user456" else None
        api.get_reservation_details.side_effect = lambda rid: reservation if rid == "resv2" else None
        api.get_flight_status.side_effect = lambda fn, date: "cancelled" if fn == "FL456" and date == "2024-06-02" else "on time"

        with pytest.raises(PolicyViolationException):
            guard_compensation_for_cancelled_or_delayed_flights(api, user_id="user456", amount=100)