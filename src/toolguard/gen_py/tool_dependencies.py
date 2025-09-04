from typing import Set
from toolguard.data_types import Domain, ToolPolicyItem
from toolguard.gen_py.prompts.analyze_dependencies import extract_api_dependencies_from_pseudo_code
from toolguard.gen_py.prompts.pseudo_code import tool_policy_pseudo_code


async def tool_dependencies(policy_item: ToolPolicyItem, tool_signature: str, domain:Domain) -> Set[str]:
    pseudo_code = await tool_policy_pseudo_code(policy_item, tool_signature, domain)
    dep_tools = await extract_api_dependencies_from_pseudo_code(pseudo_code, domain)
    return set(dep_tools)