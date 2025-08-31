from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_cabin_uniformity_requirement import guard_cabin_uniformity_requirement
from airline.airline_types import *
from airline.i_airline import *

def test_all_flights_same_cabin_economy():
    """
    Policy: "Cabin class must be the same across all flights in a reservation."
    Example: "A user updates a reservation so all flights are reassigned to economy class, ensuring uniform cabin class and complying with the policy."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="ZFA04Y",
        user_id="user123",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="economy",
        flights=[
            ReservationFlight(flight_number="HAT001", origin="SFO", destination="JFK", date="2024-06-01", price=300),
            ReservationFlight(flight_number="HAT002", origin="JFK", destination="SFO", date="2024-06-10", price=320)
        ],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ZFA04Y" else None

    flights = [
        FlightInfo(flight_number="HAT001", date="2024-06-01"),
        FlightInfo(flight_number="HAT002", date="2024-06-10")
    ]

    try:
        guard_cabin_uniformity_requirement(api, reservation_id="ZFA04Y", cabin="economy", flights=flights, payment_id="credit_card_123")
    except PolicyViolationException:
        pytest.fail("Test failed: Expected compliance but got PolicyViolationException")

def test_all_flights_same_cabin_business():
    """
    Policy: "Cabin class must be the same across all flights in a reservation."
    Example: "The reservation is modified to have all flights in business class, maintaining a consistent cabin class across the entire reservation as per the policy."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="ABC123",
        user_id="user456",
        origin="LAX",
        destination="ORD",
        flight_type="round_trip",
        cabin="business",
        flights=[
            ReservationFlight(flight_number="BUS001", origin="LAX", destination="ORD", date="2024-07-01", price=800),
            ReservationFlight(flight_number="BUS002", origin="ORD", destination="LAX", date="2024-07-10", price=820)
        ],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "ABC123" else None

    flights = [
        FlightInfo(flight_number="BUS001", date="2024-07-01"),
        FlightInfo(flight_number="BUS002", date="2024-07-10")
    ]

    try:
        guard_cabin_uniformity_requirement(api, reservation_id="ABC123", cabin="business", flights=flights, payment_id="credit_card_456")
    except PolicyViolationException:
        pytest.fail("Test failed: Expected compliance but got PolicyViolationException")

def test_round_trip_same_cabin_economy():
    """
    Policy: "Cabin class must be the same across all flights in a reservation."
    Example: "Both flight segments in a round-trip reservation are changed to the same cabin class, such as economy, meeting the Cabin Uniformity Requirement."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RT1234",
        user_id="user789",
        origin="SEA",
        destination="MIA",
        flight_type="round_trip",
        cabin="economy",
        flights=[
            ReservationFlight(flight_number="ECO001", origin="SEA", destination="MIA", date="2024-08-01", price=400),
            ReservationFlight(flight_number="ECO002", origin="MIA", destination="SEA", date="2024-08-15", price=420)
        ],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "RT1234" else None

    flights = [
        FlightInfo(flight_number="ECO001", date="2024-08-01"),
        FlightInfo(flight_number="ECO002", date="2024-08-15")
    ]

    try:
        guard_cabin_uniformity_requirement(api, reservation_id="RT1234", cabin="economy", flights=flights, payment_id="credit_card_789")
    except PolicyViolationException:
        pytest.fail("Test failed: Expected compliance but got PolicyViolationException")

def test_mixed_cabin_classes_economy_business():
    """
    Policy: "Cabin class must be the same across all flights in a reservation."
    Example: "A reservation is updated with mixed cabin classes, such as economy and business, across different flights within the same reservation. This violates the policy requiring uniform cabin class."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="MIX001",
        user_id="user321",
        origin="BOS",
        destination="ATL",
        flight_type="round_trip",
        cabin="economy",
        flights=[
            ReservationFlight(flight_number="MIXECO", origin="BOS", destination="ATL", date="2024-09-01", price=350),
            ReservationFlight(flight_number="MIXBUS", origin="ATL", destination="BOS", date="2024-09-10", price=900)
        ],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "MIX001" else None

    flights = [
        FlightInfo(flight_number="MIXECO", date="2024-09-01"),
        FlightInfo(flight_number="MIXBUS", date="2024-09-10")
    ]

    with pytest.raises(PolicyViolationException):
        guard_cabin_uniformity_requirement(api, reservation_id="MIX001", cabin="economy", flights=flights, payment_id="credit_card_321")

def test_mixed_cabin_classes_economy_basic():
    """
    Policy: "Cabin class must be the same across all flights in a reservation."
    Example: "A user changes one flight to economy and another to basic economy within a reservation, failing the Cabin Uniformity Requirement that mandates the same cabin class for all flights."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="MIX002",
        user_id="user654",
        origin="DFW",
        destination="LAS",
        flight_type="round_trip",
        cabin="economy",
        flights=[
            ReservationFlight(flight_number="ECO123", origin="DFW", destination="LAS", date="2024-10-01", price=200),
            ReservationFlight(flight_number="BAS456", origin="LAS", destination="DFW", date="2024-10-05", price=150)
        ],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "MIX002" else None

    flights = [
        FlightInfo(flight_number="ECO123", date="2024-10-01"),
        FlightInfo(flight_number="BAS456", date="2024-10-05")
    ]

    with pytest.raises(PolicyViolationException):
        guard_cabin_uniformity_requirement(api, reservation_id="MIX002", cabin="economy", flights=flights, payment_id="credit_card_654")