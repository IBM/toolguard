from typing import *
import airline
from rt_toolguard.data_types import ChatHistory
from airline.airline_types import *
from airline.i_airline import I_Airline

class PolicyViolationException(Exception):
    pass

def guard_cabin_change_payment_requirement(history: ChatHistory, api: I_Airline, reservation_id: str, cabin: Literal['business', 'economy', 'basic_economy'], flights: list[FlightInfo | dict], payment_id: str):
    """
    Policy to check: ToolX can be used to modify a reservation's cabin class. Ensure a uniform cabin class change across all flights within the reservation. Make sure the user pays the fare difference between the current cabin class and the new cabin class for the entire reservation as partial changes are disallowed.

    Args:
        history (ChatHistory): provide question-answer services over the past chat messages.
        api (I_Airline): api to access other tools.
        reservation_id: The reservation ID, such as 'ZFA04Y'.
        cabin: The cabin class of the reservation
        flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if the a flight segment is not changed, it should still be included in the array.
        payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.
    """
    # Retrieve reservation details
    reservation = api.get_reservation_details(reservation_id)

    # Ensure all flights in the reservation are included in the update
    if len(flights) != len(reservation.flights):
        raise PolicyViolationException("All flight segments must be included in the cabin change request.")

    # Check if all flights have the same cabin class
    for flight in flights:
        if isinstance(flight, FlightInfo):
            flight_instance = api.get_flight_instance(flight.flight_number, flight.date)
            if flight_instance.status != 'available':
                raise PolicyViolationException("Flight is not available for booking.")
            if cabin not in flight_instance.available_seats:
                raise PolicyViolationException(f"Cabin class {cabin} is not available for flight {flight.flight_number}.")
        elif isinstance(flight, dict):
            if flight.get('cabin') != cabin:
                raise PolicyViolationException("Cabin class change is not uniform across all flights.")

    # Calculate total fare difference
    total_fare_difference = 0
    for flight in reservation.flights:
        flight_instance = api.get_flight_instance(flight.flight_number, flight.date)
        if flight_instance.status == 'available':
            current_price = flight_instance.prices[reservation.cabin]
            new_price = flight_instance.prices[cabin]
            fare_difference = new_price - current_price
            total_fare_difference += fare_difference

    # Check payment method
    user_details = api.get_user_details(reservation.user_id)
    payment_method = user_details.payment_methods.get(payment_id)
    if not payment_method:
        raise PolicyViolationException("Payment method not found.")

    if isinstance(payment_method, GiftCard) and payment_method.amount < total_fare_difference:
        raise PolicyViolationException("Gift card balance is insufficient to cover the fare difference.")
    elif isinstance(payment_method, Certificate) and payment_method.amount < total_fare_difference:
        raise PolicyViolationException("Certificate balance is insufficient to cover the fare difference.")
    elif isinstance(payment_method, CreditCard):
        # Assume credit card has sufficient funds
        pass
    else:
        raise PolicyViolationException("Invalid payment method.")