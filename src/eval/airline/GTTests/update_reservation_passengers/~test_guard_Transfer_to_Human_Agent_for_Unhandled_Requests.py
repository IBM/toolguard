import unittest
from unittest.mock import MagicMock, patch

# Importing necessary modules
from my_app.update_reservation_passengers.guard_update_reservation_passengers import guard_update_reservation_passengers
from my_app.common import *
from my_app.domain import *


class TestGuardTransferToHumanAgentForUnhandledRequests(unittest.TestCase):
    
    # Compliance test: A user updates passenger details without changing the number of passengers.
    # "A user updates passenger details for reservation_id 'D4E5F6' by correcting the spelling of 'Jane Doe' to 'Janet Doe' and updating her DOB from '1989-12-31' to '1989-11-30'. The number of passengers remains unchanged."
    def test_update_passenger_details_without_changing_count(self):
        args = UpdateReservationPassengersRequest(reservation_id='D4E5F6', passengers=[
            Passenger3(first_name='Janet', last_name='Doe', dob='1989-11-30')
        ])
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse(root={})
        api.search_direct_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.search_onestop_flight.return_value = []
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()
        api.get_reservation_details.return_value = GetReservationDetailsResponse()

        guard_update_reservation_passengers(args, history, api)

    # Violation test: A user tries to add a new passenger, changing the number of passengers.
    # "A user tries to update the reservation with reservation_id 'A1B2C3' to add a new passenger 'John Doe' with DOB '1990-01-01'. This violates the policy as it changes the number of passengers in the reservation."
    def test_add_new_passenger_violates_policy(self):
        args = UpdateReservationPassengersRequest(reservation_id='A1B2C3', passengers=[
            Passenger3(first_name='John', last_name='Doe', dob='1990-01-01')
        ])
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse(root={})
        api.search_direct_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.search_onestop_flight.return_value = []
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()
        api.get_reservation_details.return_value = GetReservationDetailsResponse()

        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when adding a new passenger."):
            guard_update_reservation_passengers(args, history, api)

    # Compliance test: Changing passenger details without altering the count.
    # "The reservation with id 'GHJ123' has two passengers, and the request comes to change the date of birth for 'Michael Smith', maintaining the initial number of passengers."
    def test_change_dob_without_changing_passenger_count(self):
        args = UpdateReservationPassengersRequest(reservation_id='GHJ123', passengers=[
            Passenger3(first_name='Michael', last_name='Smith', dob='1990-01-01')
        ])
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse(root={})
        api.search_direct_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.search_onestop_flight.return_value = []
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()
        api.get_reservation_details.return_value = GetReservationDetailsResponse()

        guard_update_reservation_passengers(args, history, api)

    # Violation test: Attempting to remove a passenger.
    # "Attempting to remove an existing passenger from reservation_id 'X9Y8Z7'. The user wants to update the reservation by removing 'Anna Smith', DOB '1985-07-12'. This alteration affects the passenger count, violating the policy."
    def test_remove_passenger_violates_policy(self):
        args = UpdateReservationPassengersRequest(reservation_id='X9Y8Z7', passengers=[])
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse(root={})
        api.search_direct_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.search_onestop_flight.return_value = []
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()
        api.get_reservation_details.return_value = GetReservationDetailsResponse()

        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when removing a passenger."):
            guard_update_reservation_passengers(args, history, api)

    # Compliance test: Swapping last names without changing passenger count.
    # "A user submits a change request for reservation_id 'PQR789', swapping the last name of 'Emma Wilson' to 'Emma Thompson', with no change to the count of passengers."
    def test_swap_last_name_without_changing_count(self):
        args = UpdateReservationPassengersRequest(reservation_id='PQR789', passengers=[
            Passenger3(first_name='Emma', last_name='Thompson', dob='1990-01-01')
        ])
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse(root={})
        api.search_direct_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.search_onestop_flight.return_value = []
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()
        api.get_reservation_details.return_value = GetReservationDetailsResponse()

        guard_update_reservation_passengers(args, history, api)

    # Violation test: Adding a fourth passenger.
    # "A request arrives with reservation_id 'LMN123' where the user wants to change three passengers' details but also add a fourth passenger, 'Gary Brown', which changes the total number of passengers in the reservation."
    def test_add_fourth_passenger_violates_policy(self):
        args = UpdateReservationPassengersRequest(reservation_id='LMN123', passengers=[
            Passenger3(first_name='Gary', last_name='Brown', dob='1990-01-01')
        ])
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse(root={})
        api.search_direct_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.search_onestop_flight.return_value = []
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()
        api.get_reservation_details.return_value = GetReservationDetailsResponse()

        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when adding a fourth passenger."):
            guard_update_reservation_passengers(args, history, api)

    # Compliance test: Updating DOBs without altering passenger count.
    # "Modifying reservation_id 'TUV567' only to update incorrectly entered DOBs for all passengers without adding, removing, or otherwise altering the passenger count. The policy is fully respected."
    def test_update_dobs_without_changing_count(self):
        args = UpdateReservationPassengersRequest(reservation_id='TUV567', passengers=[
            Passenger3(first_name='Noah', last_name='Brown', dob='1990-01-01')
        ])
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse(root={})
        api.search_direct_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.search_onestop_flight.return_value = []
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()
        api.get_reservation_details.return_value = GetReservationDetailsResponse()

        guard_update_reservation_passengers(args, history, api)

    # Violation test: Decreasing passenger count.
    # "A request to update reservation_id 'XYZ789' by substituting an existing passenger 'Helen Cooper' with 'Sarah Cooper'. However, additional details about other passengers indicate a decrease in count, thus violating the policy."
    def test_decrease_passenger_count_violates_policy(self):
        args = UpdateReservationPassengersRequest(reservation_id='XYZ789', passengers=[
            Passenger3(first_name='Sarah', last_name='Cooper', dob='1990-01-01')
        ])
        history = MagicMock()
        history.ask_bool.return_value = True

        api = MagicMock()
        api.get_user_details.return_value = GetUserDetailsResponse()
        api.list_all_airports.return_value = ListAllAirportsResponse(root={})
        api.search_direct_flight.return_value = []
        api.get_flight_details.return_value = ''
        api.search_onestop_flight.return_value = []
        api.get_flight_on_date_details.return_value = GetFlightOnDateDetailsResponse()
        api.get_reservation_details.return_value = GetReservationDetailsResponse()

        with self.assertRaises(PolicyViolationException, msg="Expected PolicyViolationException when decreasing passenger count."):
            guard_update_reservation_passengers(args, history, api)


if __name__ == '__main__':
    unittest.main()
