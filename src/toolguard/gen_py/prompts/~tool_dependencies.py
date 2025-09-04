
from typing import List
from toolguard.data_types import Domain, ToolPolicyItem
from programmatic_ai import generative


@generative
async def tool_dependencies(policy_item: ToolPolicyItem, tool_signature: str, domain: Domain) -> List[str]:
    """
Identify the names of other tools that the given tool relies on, according to its business policy.

Parameters:
    * policy_item (ToolPolicyItem): A natural-language business rule that specifies a constraint on how the tool under analysis should be used.
    * tool_signature (str): The tool’s function signature, including its documentation and parameters.
    * domain (Domain): Python definitions of the available tool names (API function names) and their associated data types.

Output:
    * List[str]: A list of tool names that the analyzed tool depends on.

Implementation Guidelines:
    * A dependency exists if another tool must be called in order to enforce the given policy when invoking the tool under analysis.
    * Direct dependencies occur when a tool can be invoked directly to supply missing data, to transform or map the data, or to validate constraints.
    * Indirect dependencies may involve chains of calls, repeated invocations of the same tool, or comparisons between old and new states (e.g., when updating data).
        Examples of Indirect Dependencies:
        * Calling a validation API once per list item.
        * Fetching both the existing state and the new state when updates are involved (e.g., verifying a hotel reservation update requires both get_hotel_reservation and get_room_details).

Constraint:
    * A tool may only depend on immutable (read-only) tools.

Examples:
    ```python
    domain = {
        "app_types": {
            "file_name": "car_types.py",
            "content": '''
                class Car:
                    plate_num: str
                    previous_owner_ids: List[str]
                class Person:
                    id: str
                    driving_licence: str
                class Insurance:
                    doc_id: str
            '''
        },
        "app_api": {
            "file_name": "cars_api.py",
            "content": '''
                class CarAPI(ABC):
                    def buy_car(self, plate_num: str, owner_id: str, insurance_id: str): pass
                    def get_person(self, id: str) -> Person: pass
                    def get_insurance(self, id: str) -> Insurance: pass
                    def get_car(self, plate_num: str) -> Car: pass
                    def delete_car(self, plate_num: str): pass
                    def list_all_cars_owned_by(self, id: str) -> List[Car]: pass
                    def are_relatives(self, person1_id: str, person2_id: str) -> bool: pass
            '''
        }
    }

    assert tool_dependencies(
        {"name": "documents exists", "description": "when buying a car, check that the car owner has a driving licence and that the insurance is valid."},
        "buy_car(plate_num: str, owner_id: str, insurance_id: str)",
        domain
    ) == ["get_person", "get_insurance"]

    assert tool_dependencies(
        {"name": "has driving licence", "description": "when buying a car, check that the car owner has a driving licence"},
        "buy_car(plate_num: str, owner_id: str, insurance_id: str)",
        domain
    ) == ["get_person"]

    assert tool_dependencies(
        {"name": "no transfers on holidays", "description": "when buying a car, check that it is not a holiday today"},
        "buy_car(plate_num: str, owner_id: str, insurance_id: str)",
        domain
    ) == []

    # Indirect dependency. are_relatives() should be called multiple times.
    assert tool_dependencies(
        {"name": "Not in the same family", "description": "when buying a car, check that the car was never owned by someone from the buyer's family."},
        "buy_car(plate_num: str, owner_id: str, insurance_id: str)",
        domain
    ) == ["get_car", "are_relatives"]
    ```
"""
    ...
