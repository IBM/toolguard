import copy
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal, Tuple

import yaml

from policy_adherence.common.dict import substitute_refs
from policy_adherence.llm.azure_wrapper import AzureLitellm, AzureWrepper
from policy_adherence.llm.llm_model import LLM_model
# from policy_adherence.jschema.json_schema import JSONSchemaModel
from policy_adherence.oas.OAS import OpenAPI, Operation, PathItem, Schema
# from policy_adherence.oas.oas_dom import OASModel
# from policy_adherence.oas.remove_orphan_comps import remove_orphan_components

load_dotenv()

class Code(BaseModel):
    file_name: str
    content: str


class ToolPolicyItem(BaseModel):
    policy: str = Field(..., description="Policy item")
    compliance_examples: Optional[List[str]] = Field(..., description="Case example that complies with the policy")
    violation_examples: Optional[List[str]] = Field(..., description="Case example that violates the policy")
class ToolInfo(BaseModel):
    tool_name: str = Field(..., description="Tool name")
    tool_description: str = Field(..., description="Tool description")
    policy_items: List[ToolPolicyItem]
    # tool_input_schema: Schema = Field(..., description="Tool Input schema")
    # tool_output_schema: Schema = Field(..., description="Tool output schema")


def fn_is_ok(fn_code: Code, domain: Code, test_cases:Code, llm: LLM_model):
    return True
    # compilation
    # lint
    # hallucinations
    # llm all poliCIES ARE COVERED?
    # llm code that is not described in policy?
    # testcases

def extract_code_from_response(resp:str)->str:
    start_code_token = "```python\n"
    end_code_token = "```\n\n"
    start = resp.find(start_code_token) + len(start_code_token)
    end = resp.find(end_code_token)
    return resp[start:end]

def generate_signatures(oas: OpenAPI, llm: LLM_model)->Code:
    prompt = f"""Given an OpenAPI Spec, generate Python code that include all the data types as pydantic classes. 
For each operation, create astub function, named by the operationId, with the function description, inputs and outputs.

{oas.model_dump_json(indent=2)}
"""
    msgs = [{"role":"system", "content": prompt}]
    res = llm.chat_json(msgs)
    res_content = res.choices[0].message.content
    code = Code(
        file_name="domain.py",
        content=extract_code_from_response(res_content)
    )
    return code


def policy_statements(tool: ToolInfo):
    s = ""
    for item in tool.policy_items:
        s+= f"## {item.policy}\n"
        if item.compliance_examples:
            s+="### Positive examples\n"
            for pos_ex in item.compliance_examples:
                s+=f"* {pos_ex}\n"
        if item.violation_examples:
            s+="### Negative examples\n"
            for neg_ex in item.violation_examples:
                s+=f"* {neg_ex}\n"
        s+="\n"
    return s

def generate_test_cases(signatures:Code, tool: ToolInfo, llm: LLM_model)-> Code:
    prompt = f"""You are given a domain definitions in Python.
You need to generate test cases for the function under test: {tool.tool_name}(). 

You are also given with policy statement that and the function under test should comply with.
For each statement, you are given with positive and negative test case examples,    
For negative cases check that the funtion under test raise an exception. 
For positive cases check that no exception raised.

# Domain defintion
# in `{signatures.file_name}` file.
{signatures.content}

# Policy statements
    {policy_statements(tool)}
"""
    msgs = [{"role":"system", "content": prompt}]
    res = llm.chat_json(msgs)
    res_content = res.choices[0].message.content
    code = Code(
        file_name=f"test_check_{tool.tool_name}.py",
        content=extract_code_from_response(res_content)
    )
    return code

def _generate_validation_fn_code(domain: Code, tool_info:ToolInfo, llm: LLM_model)->Code:
    prompt = f"""You are given domain with data classes and functions.
You are also given with a list of policy items. Policy items have a list of positive and negative examples. 
You need to implement a function `check_{tool_info.tool_name}()` with signature identical to {tool_info.tool_name}()`.
The function implementation should check that all the policy items are holds. 
Running the code on the positive examples should pass normally. 
Running the code on the negative examples should rais an exception.

# Domain definition (in `{domain.file_name}`):
```
{domain.content}
```

# Policy Items:
{policy_statements(tool_info)}
"""
    msgs = [{"role":"system", "content": prompt}]
    res = llm.chat_json(msgs)
    res_content = res.choices[0].message.content
    return Code(
        file_name=f"check_{tool_info.tool_name}.py", 
        content=extract_code_from_response(res_content)
    )

def generate_validation_fn_code(domain: Code, tool_info:ToolInfo, llm: LLM_model)->Tuple[Code, Code]:
    test_cases = generate_test_cases(domain, tool_info, llm)
    try_idx, max_try = 0, 1
    valid_fn_code = _generate_validation_fn_code(domain, tool_info, llm)
    while not fn_is_ok(valid_fn_code, domain, test_cases, llm) and try_idx< max_try:
        valid_fn_code = _generate_validation_fn_code(domain, tool_info, llm)
        try_idx += 1

    return valid_fn_code, test_cases

def save_codes(folder:str, codes: List[Code]):
    os.makedirs(folder, exist_ok=True)
    for code in codes:
        file_path = os.path.join(folder, code.file_name)
        with open(file_path, "w") as file:
            file.write(code.content)

def read_oas(file_path:str)->OpenAPI:
    with open(file_path, "r") as file:
        d = yaml.safe_load(file)
    oas = OpenAPI.model_validate(d)
    return oas

def load_policy(file_path:str)->List[ToolPolicyItem]:
    with open(file_path, "r") as file:
        d = json.load(file)
    
    policies = d.get("policies", [])
    policy_items = []
    for i, p in enumerate(policies):
        policy_items.append(
            ToolPolicyItem(
                policy = p.get(f"policy description {i+1}"),
                compliance_examples = p.get(f"Compliance Examples {i+1}"),
                violation_examples = p.get(f"Violating Examples {i+1}")
            )
        )
    return policy_items

def op_only_oas(oas: OpenAPI, operationId: str)-> OpenAPI:
    new_oas = OpenAPI(
        openapi=oas.openapi, 
        info=oas.info,
        components=oas.components
    )
    for path, path_item in oas.paths.items():
        for mtd, op in path_item.operations.items():
            if op.operationId == operationId:
                if new_oas.paths.get(path) is None:
                    new_oas.paths[path] = PathItem(
                        summary=path_item.summary,
                        description=path_item.description,
                        servers=path_item.servers,
                        parameters=path_item.parameters,
                    ) # type: ignore
                setattr(
                    new_oas.paths.get(path), 
                    mtd.lower(), 
                    copy.deepcopy(op)
                )
                op = Operation(**(substitute_refs(op.model_dump())))
    return new_oas
    
def main():
    oas_path = "tau_airline/input/openapi.yml"
    tool_names = ["book_reservation"]
    policy_paths = ["tau_airline/input/BookReservation_fix_5.json"]
    model = "gpt-4o-2024-08-06"

    policies = [load_policy(path) for path in policy_paths]
    oas = read_oas(oas_path)
    llm = AzureLitellm(model)

    domain = generate_signatures(oas, llm)
    save_codes("tau_airline/output", [domain])
    for tool_name, tool_poilcy_items in zip(tool_names, policies):
        if len(tool_poilcy_items) == 0: continue
        op_oas = op_only_oas(oas, tool_name)
        op = op_oas.get_operation_by_operationId(tool_name)
        assert op
        tool_info = ToolInfo(
            tool_name=tool_name, 
            tool_description=op.description,
            policy_items=tool_poilcy_items
            # tool_input_schema=op.requestBody.content_json.schema_,
            # tool_output_schema=op.responses.get("200").content_json.schema_
        )

        code, tests = generate_validation_fn_code(domain, tool_info, llm)
        save_codes("tau_airline/output", [code, tests])

if __name__ == '__main__':
    main()