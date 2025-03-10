import ast
import copy
from datetime import datetime
import json
import os
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple

from policy_adherence.common.dict import substitute_refs
from policy_adherence.llm.azure_wrapper import AzureLitellm
from policy_adherence.llm.llm_model import LLM_model
from policy_adherence.oas import OpenAPI, Operation, PathItem

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
    end_code_token = "```"
    start = resp.find(start_code_token) + len(start_code_token)
    end = resp.rfind(end_code_token)
    return resp[start:end]

def generate_domain(oas: OpenAPI, llm: LLM_model)->Code:
    prompt = f"""Given an OpenAPI Spec, generate Python code that include all the data types as pydantic classes. 
For each operation, create astub function, named by the operationId, with the function description, argument types and return type.

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
    for i, item in enumerate(tool.policy_items):
        s+= f"## Policy item {i+1}"
        s+=f"{item.policy}\n"
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

def check_tool_function_stub(code:str, fn_name:str, new_fn_name:str)->Optional[str]:
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            node.name = new_fn_name
            node.returns = ast.Constant(value=None)
            node.body = [ast.Pass()]
            return ast.unparse(node)

def generate_test_cases(domain:Code, tool: ToolInfo, llm: LLM_model)-> Code:
    tool_name = tool.tool_name
    fn_under_test = check_tool_function_stub(domain.content, tool_name, f"check_{tool_name}")
    prompt = f"""Given the below function in Python:
```
### check_{tool_name}.py
{fn_under_test}
```
You are given a domain definitions in Python.
```
### {domain.file_name}
{domain.content}
```

You are also given with policy statement that and the function under test should comply with.
For each statement, you are given with positive and negative test case examples,    
For negative cases check that the funtion under test raise an exception. 
For positive cases check that no exception raised.

{policy_statements(tool)}

Generate test cases for the function under test. 
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
    now = datetime.now()
    output_path = f"tau_airline/output/{now.strftime("%Y-%m-%d %H:%M:%S")}"

    policies = [load_policy(path) for path in policy_paths]
    oas = read_oas(oas_path)
    llm = AzureLitellm(model)

    domain = generate_domain(oas, llm)
    save_codes(output_path, [domain])
    for tool_name, tool_poilcy_items in zip(tool_names, policies):
        if len(tool_poilcy_items) == 0: continue
        # op_oas = op_only_oas(oas, tool_name)
        op = oas.get_operation_by_operationId(tool_name)
        assert op
        tool_info = ToolInfo(
            tool_name=tool_name, 
            tool_description=op.description,
            policy_items=tool_poilcy_items
        )

        code, tests = generate_validation_fn_code(domain, tool_info, llm)
        save_codes(output_path, [code, tests])

if __name__ == '__main__':
    load_dotenv()
    main()