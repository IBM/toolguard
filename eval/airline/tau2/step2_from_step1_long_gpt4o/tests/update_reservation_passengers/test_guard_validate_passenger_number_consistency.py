from unittest.mock import MagicMock, patch
import pytest
from rt_toolguard.data_types import PolicyViolationException
from airline.update_reservation_passengers.guard_validate_passenger_number_consistency import guard_validate_passenger_number_consistency
from airline.i_airline import *
from airline.airline_types import *

class TestGuardValidatePassengerNumberConsistency:

    def test_update_passenger_details_maintain_count(self):
        """
        Policy: "When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same."
        Example: "A user updates the reservation 'ZFA04Y', originally for 3 passengers, by changing the name and date of birth of a passenger while maintaining the total number unchanged."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API and its return values
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
                Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
                Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03")
            ],
            payment_history=[],
            created_at="2023-10-01T12:00:00",
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        guard_validate_passenger_number_consistency(
            history=history,
            api=api,
            reservation_id="ZFA04Y",
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
                Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
                Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03")
            ]
        )

    def test_violate_passenger_number_by_removal(self):
        """
        Policy: "When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same."
        Example: "A user attempts to update a reservation with ID 'ZFA04Y', initially having 3 passengers, to an updated list containing only 2 passengers."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API and its return values
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
                Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
                Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03")
            ],
            payment_history=[],
            created_at="2023-10-01T12:00:00",
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_validate_passenger_number_consistency(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                passengers=[
                    Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
                    Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02")
                ]
            )

    def test_violate_passenger_number_by_addition(self):
        """
        Policy: "When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same."
        Example: "A user tries to modify the reservation 'ZFA04Y' by adding a fourth passenger when the reservation originally included 3 passengers."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API and its return values
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
                Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
                Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03")
            ],
            payment_history=[],
            created_at="2023-10-01T12:00:00",
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_validate_passenger_number_consistency(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                passengers=[
                    Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
                    Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
                    Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03"),
                    Passenger(first_name="Jack", last_name="Daniels", dob="1980-04-04")
                ]
            )

    def test_violate_passenger_number_by_excess(self):
        """
        Policy: "When modifying passenger details in a reservation using ToolX, ensure the number of passengers remains the same."
        Example: "User requests an update on reservation 'ZFA04Y' by submitting a list of 5 passengers, while the original reservation only contained 4."
        """
        
        # Mock the history service
        history = MagicMock()
        history.ask_bool.return_value = True

        # Mock the API and its return values
        reservation = Reservation(
            reservation_id="ZFA04Y",
            user_id="user123",
            origin="SFO",
            destination="JFK",
            flight_type="round_trip",
            cabin="economy",
            flights=[],
            passengers=[
                Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
                Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
                Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03"),
                Passenger(first_name="Jack", last_name="Daniels", dob="1980-04-04")
            ],
            payment_history=[],
            created_at="2023-10-01T12:00:00",
            total_baggages=2,
            nonfree_baggages=1,
            insurance="yes",
            status=None
        )

        api = MagicMock(spec=I_Airline)
        api.get_reservation_details.side_effect = lambda reservation_id: reservation if reservation_id == "ZFA04Y" else None

        # Invoke function under test
        with pytest.raises(PolicyViolationException):
            guard_validate_passenger_number_consistency(
                history=history,
                api=api,
                reservation_id="ZFA04Y",
                passengers=[
                    Passenger(first_name="John", last_name="Doe", dob="1990-01-01"),
                    Passenger(first_name="Jane", last_name="Doe", dob="1992-02-02"),
                    Passenger(first_name="Jim", last_name="Beam", dob="1985-03-03"),
                    Passenger(first_name="Jack", last_name="Daniels", dob="1980-04-04"),
                    Passenger(first_name="Johnny", last_name="Walker", dob="1975-05-05")
                ]
            )
