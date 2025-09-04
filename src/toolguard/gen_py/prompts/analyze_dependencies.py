
from typing import List
from toolguard.data_types import Domain
from programmatic_ai import generative


@generative
async def extract_api_dependencies_from_pseudo_code(pseuod_code: str, domain: Domain) -> List[str]:
    """
    Returns the names of the API functions used in the pseuod_code.
    """
    pass