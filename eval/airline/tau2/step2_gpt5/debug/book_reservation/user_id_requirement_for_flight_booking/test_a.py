from unittest.mock import MagicMock
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_user_id_requirement_for_flight_booking import guard_user_id_requirement_for_flight_booking
from airline.airline_types import *
from airline.i_airline import *

def test_compliance_user_id_first_then_inquiries():
    """
    Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
    Example: "The agent asks the user for their user ID before proceeding with any inquiries on trip type, origin, destination, passenger list, and payment methods, ensuring compliance."
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT001", date="2024-05-01")]
    passengers = [Passenger(first_name="John", last_name="Doe", dob="1990-01-01")]
    payments = [Payment(payment_id="pay123", amount=500)]

    try:
        guard_user_id_requirement_for_flight_booking(
            api,
            user_id="sara_doe_496",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=flights,
            passengers=passengers,
            payment_methods=payments,
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes"
        )
    except PolicyViolationException:
        pytest.fail("Compliance scenario failed: Expected no PolicyViolationException, but one was raised.")

def test_compliance_user_id_validated_first():
    """
    Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
    Example: "User ID is obtained and validated first, followed by inquiries about flight type, cabin class, and insurance coverage, maintaining the correct sequence as per policy."
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT002", date="2024-06-01")]
    passengers = [Passenger(first_name="Alice", last_name="Smith", dob="1985-05-05")]
    payments = [Payment(payment_id="pay456", amount=300)]

    try:
        guard_user_id_requirement_for_flight_booking(
            api,
            user_id="john_smith_123",
            origin="LAX",
            destination="ORD",
            flight_type="one_way",
            cabin="business",
            flights=flights,
            passengers=passengers,
            payment_methods=payments,
            total_baggages=1,
            nonfree_baggages=0,
            insurance="no"
        )
    except PolicyViolationException:
        pytest.fail("Compliance scenario failed: Expected no PolicyViolationException, but one was raised.")

def test_compliance_confirm_user_id_then_flight_details():
    """
    Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
    Example: "Upon confirming the user's ID, such as 'sara_doe_496', the agent systematically handles inquiries about flight specifics, ensuring compliance through verification of user ID first."
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT003", date="2024-07-01")]
    passengers = [Passenger(first_name="Bob", last_name="Brown", dob="1970-12-12")]
    payments = [Payment(payment_id="pay789", amount=700)]

    try:
        guard_user_id_requirement_for_flight_booking(
            api,
            user_id="sara_doe_496",
            origin="SEA",
            destination="MIA",
            flight_type="round_trip",
            cabin="basic_economy",
            flights=flights,
            passengers=passengers,
            payment_methods=payments,
            total_baggages=3,
            nonfree_baggages=2,
            insurance="yes"
        )
    except PolicyViolationException:
        pytest.fail("Compliance scenario failed: Expected no PolicyViolationException, but one was raised.")

def test_violation_booking_without_user_id():
    """
    Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
    Example: "The agent proceeds to book a flight without first obtaining the user ID, starting inquiries directly with the trip type, origin, and destination, which violates the policy of collecting user ID first."
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT004", date="2024-08-01")]
    passengers = [Passenger(first_name="Charlie", last_name="Davis", dob="1995-03-03")]
    payments = [Payment(payment_id="pay101", amount=400)]

    with pytest.raises(PolicyViolationException):
        guard_user_id_requirement_for_flight_booking(
            api,
            user_id="",
            origin="BOS",
            destination="ATL",
            flight_type="one_way",
            cabin="economy",
            flights=flights,
            passengers=passengers,
            payment_methods=payments,
            total_baggages=1,
            nonfree_baggages=0,
            insurance="no"
        )

def test_violation_payment_and_flight_without_user_id():
    """
    Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
    Example: "Booking is initiated with discussions about payment methods, flight details, and cabin preferences without confirming the user ID beforehand, contrary to policy requirements."
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT005", date="2024-09-01")]
    passengers = [Passenger(first_name="Dana", last_name="Evans", dob="1988-08-08")]
    payments = [Payment(payment_id="pay202", amount=600)]

    with pytest.raises(PolicyViolationException):
        guard_user_id_requirement_for_flight_booking(
            api,
            user_id=None,
            origin="DFW",
            destination="LAS",
            flight_type="round_trip",
            cabin="business",
            flights=flights,
            passengers=passengers,
            payment_methods=payments,
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes"
        )

def test_violation_insurance_and_baggage_without_user_id():
    """
    Policy: "The agent must first obtain the user ID before proceeding with flight booking and subsequent inquiries for trip type, origin, and destination."
    Example: "The agent asks for insurance preferences, baggage information, and passenger count directly without verifying the user ID at the start, failing to adhere to user ID sequence policy."
    """
    api = MagicMock(spec=I_Airline)
    flights = [FlightInfo(flight_number="HAT006", date="2024-10-01")]
    passengers = [Passenger(first_name="Eve", last_name="Foster", dob="1992-11-11")]
    payments = [Payment(payment_id="pay303", amount=800)]

    with pytest.raises(PolicyViolationException):
        guard_user_id_requirement_for_flight_booking(
            api,
            user_id="   ",
            origin="PHX",
            destination="DEN",
            flight_type="one_way",
            cabin="basic_economy",
            flights=flights,
            passengers=passengers,
            payment_methods=payments,
            total_baggages=4,
            nonfree_baggages=3,
            insurance="no"
        )