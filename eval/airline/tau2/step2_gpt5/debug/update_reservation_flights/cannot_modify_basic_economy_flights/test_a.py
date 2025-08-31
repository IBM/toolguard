from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_flights.guard_cannot_modify_basic_economy_flights import guard_cannot_modify_basic_economy_flights
from airline.airline_types import *
from airline.i_airline import *

def test_update_business_reservation_same_route():
    """ 
    Policy: "Basic economy flights in a reservation cannot be modified at all. For reservations that are not classified as basic economy, modifications are allowed but must not change the origin, destination, or trip type."
    Example: "An agent successfully updates a 'business' reservation by changing the flight times, keeping the same origin 'SFO' and destination 'JFK' without altering the trip type from 'round_trip', ensuring compliance with the policy."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RES123",
        user_id="USER1",
        origin="SFO",
        destination="JFK",
        flight_type="round_trip",
        cabin="business",
        flights=[ReservationFlight(flight_number="FL123", date="2024-06-01", price=500, origin="SFO", destination="JFK")],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "RES123" else None
    api.get_scheduled_flight.side_effect = lambda fn: Flight(
        flight_number=fn,
        origin="SFO",
        destination="JFK",
        scheduled_departure_time_est="06:00:00",
        scheduled_arrival_time_est="14:00:00",
        dates={}
    )
    flights = [FlightInfo(flight_number="FL123", date="2024-06-01")]
    guard_cannot_modify_basic_economy_flights(api, "RES123", "business", flights, "pay123")

def test_change_basic_economy_origin_destination():
    """ 
    Policy: "Basic economy flights in a reservation cannot be modified at all."
    Example: "A user attempts to change a reservation with basic economy flights by providing a new itinerary with updated origin and destination details, violating the restriction on modifying basic economy flights."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RES456",
        user_id="USER2",
        origin="LAX",
        destination="ORD",
        flight_type="round_trip",
        cabin="basic_economy",
        flights=[ReservationFlight(flight_number="FL456", date="2024-06-10", price=300, origin="LAX", destination="ORD")],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=0,
        nonfree_baggages=0,
        insurance="no",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "RES456" else None
    api.get_scheduled_flight.side_effect = lambda fn: Flight(
        flight_number=fn,
        origin="SFO",
        destination="JFK",
        scheduled_departure_time_est="08:00:00",
        scheduled_arrival_time_est="16:00:00",
        dates={}
    )
    flights = [FlightInfo(flight_number="FL789", date="2024-06-10")]
    with pytest.raises(PolicyViolationException):
        guard_cannot_modify_basic_economy_flights(api, "RES456", "basic_economy", flights, "pay456")

def test_change_trip_type_for_economy():
    """ 
    Policy: "For reservations that are not classified as basic economy, modifications are allowed but must not change the origin, destination, or trip type."
    Example: "An agent attempts to update a reservation classified as 'economy' by changing the trip type from 'round_trip' to 'one_way', which violates the policy of maintaining trip type for non-basic reservations."
    """
    api = MagicMock(spec=I_Airline)
    reservation = Reservation(
        reservation_id="RES789",
        user_id="USER3",
        origin="BOS",
        destination="MIA",
        flight_type="round_trip",
        cabin="economy",
        flights=[ReservationFlight(flight_number="FL321", date="2024-07-01", price=400, origin="BOS", destination="MIA")],
        passengers=[],
        payment_history=[],
        created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        total_baggages=1,
        nonfree_baggages=0,
        insurance="yes",
        status=None
    )
    api.get_reservation_details.side_effect = lambda rid: reservation if rid == "RES789" else None
    api.get_scheduled_flight.side_effect = lambda fn: Flight(
        flight_number=fn,
        origin="BOS",
        destination="MIA",
        scheduled_departure_time_est="09:00:00",
        scheduled_arrival_time_est="12:00:00",
        dates={}
    )
    flights = [FlightInfo(flight_number="FL321", date="2024-07-01")]
    with pytest.raises(PolicyViolationException):
        guard_cannot_modify_basic_economy_flights(api, "RES789", "economy", flights, "pay789")