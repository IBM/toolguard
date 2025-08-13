import json
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List

def load_openapi_spec(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r') as f:
        if file_path.endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        return json.load(f)

def sanitize_function_name(name: str) -> str:
    name = name.replace('/', '_').replace('{', '').replace('}', '')
    name = re.sub(r'[^0-9a-zA-Z_]', '_', name)
    return name.lower()

def map_openapi_type(prop: Dict[str, Any]) -> str:
    typ = prop.get("type")
    fmt = prop.get("format", "")
    if typ == "string":
        return "str"
    elif typ == "integer":
        return "int"
    elif typ == "number":
        return "float"
    elif typ == "boolean":
        return "bool"
    elif typ == "array":
        items = prop.get("items", {})
        return f"List[{map_openapi_type(items)}]"
    elif typ == "object":
        return "Dict[str, Any]"
    else:
        return "Any"

def extract_request_body_args(request_body: Dict[str, Any]) -> List[str]:
    args = []
    if not request_body:
        return args

    content = request_body.get("content", {}).get("application/json", {})
    schema = content.get("schema", {})
    required_fields = set(schema.get("required", []))
    properties = schema.get("properties", {})

    for prop_name, prop_info in properties.items():
        python_type = map_openapi_type(prop_info)
        if prop_name in required_fields:
            args.append(f"{prop_name}: {python_type}")
        else:
            args.append(f"{prop_name}: {python_type} = None")
    return args

def extract_response_type(responses: Dict[str, Any]) -> str:
    schema = (
        responses.get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    if schema.get("type") == "array":
        return "List[Dict[str, Any]]"
    elif schema.get("type") == "object":
        return "Dict[str, Any]"
    return "Any"

def generate_function_signature(path: str, method: str, operation: Dict[str, Any]) -> str:
    operation_id = operation.get('operationId')
    parameters = operation.get('parameters', [])
    request_body = operation.get('requestBody')
    responses = operation.get('responses', {})

    func_name = operation_id if operation_id else sanitize_function_name(f"{method}_{path}")

    args = []

    # Handle query/path/header parameters
    for param in parameters:
        name = param['name']
        required = param.get('required', False)
        schema = param.get("schema", {})
        python_type = map_openapi_type(schema)
        if required:
            args.append(f"{name}: {python_type}")
        else:
            args.append(f"{name}: {python_type} = None")

    # Handle request body
    args += extract_request_body_args(request_body)
    args_str = ", ".join(args) if args else ""

    # Handle return type
    return_type = extract_response_type(responses)

    # Docstring
    summary = operation.get('summary', '').strip()
    description = operation.get('description', '').strip()
    summary_line = f"{summary}" if summary else f"{method.upper()} {path}"
    full_doc = f'"""{summary_line}\n\n{description}\n"""' if summary or description else f'"""{method.upper()} {path}."""'

    return f"def {func_name}({args_str}) -> {return_type}:\n    {full_doc}\n    pass\n"

def generate_functions_from_openapi(openapi: Dict[str, Any]) -> str:
    output = ["from typing import List, Dict, Any\n"]
    for path, methods in openapi.get('paths', {}).items():
        for method, operation in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                function_code = generate_function_signature(path, method, operation)
                output.append(function_code)
    return "\n\n".join(output)

# === Example usage ===
if __name__ == '__main__':
    spec_path = "/Users/naamazwerdling/Documents/OASB/policy_validation/airline/oas3.json"
    openapi_spec = load_openapi_spec(spec_path)
    code = generate_functions_from_openapi(openapi_spec)
    Path("../policy_adherence/code_gen/typed_api_functions.py").write_text(code)
    print("Function signatures written to typed_api_functions.py")
