from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta
from rt_toolguard.data_types import PolicyViolationException
from airline.book_reservation.guard_user_confirmation_before_database_update import guard_user_confirmation_before_database_update
from airline.airline_types import *
from airline.i_airline import *

class TestGuardUserConfirmationBeforeDatabaseUpdate:

    def test_booking_with_user_confirmation(self):
        """ 
        Policy: Ensure explicit 'yes' confirmation before database updates.
        Example: Before finalizing a new reservation for Emily, including flight details, passenger names, and baggage information, the system displays all changes to Emily and obtains her explicit 'yes' confirmation to proceed with the booking.
        """
        api = MagicMock(spec=I_Airline)
        flights = [FlightInfo(flight_number="HAT001", date="2024-06-01")]
        passengers = [Passenger(first_name="Emily", last_name="Smith", dob="1990-05-05")]
        payments = [Payment(payment_id="pay123", amount=500)]

        # Should not raise exception for compliance
        guard_user_confirmation_before_database_update(
            api,
            user_id="emily_123",
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

    def test_booking_without_user_confirmation(self):
        """ 
        Policy: Ensure explicit 'yes' confirmation before database updates.
        Example: The system attempts to book a reservation and update the flight details without displaying them to the user first. John does not get the chance to review or confirm these changes before they are applied.
        """
        api = MagicMock(spec=I_Airline)
        flights = [FlightInfo(flight_number="HAT002", date="2024-06-10")]
        passengers = [Passenger(first_name="John", last_name="Doe", dob="1985-03-03")]
        payments = [Payment(payment_id="pay456", amount=300)]

        with pytest.raises(PolicyViolationException):
            guard_user_confirmation_before_database_update(
                api,
                user_id="john_456",
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