import json
from typing import Dict, List, Any

def resolve_schema_type(schema: Dict[str, Any]) -> str:
	"""Resolve type from schema, supporting anyOf and object types."""
	if "anyOf" in schema:
		return "Union[" + ", ".join(resolve_schema_type(sub) for sub in schema["anyOf"]) + "]"
	elif schema.get("type") == "array":
		item_type = resolve_schema_type(schema.get("items", {}))
		return f"List[{item_type}]"
	elif schema.get("type") == "object":
		return "Dict[str, Any]"
	return {
		"string": "str",
		"integer": "int",
		"number": "float",
		"boolean": "bool",
		"object": "Dict[str, Any]",
	}.get(schema.get("type", "Any"), "Any")


def parse_request_body(request_body: Dict[str, Any]) -> Dict[str, Any]:
	content = request_body.get("content", {}).get("application/json", {})
	schema = content.get("schema", {})
	props = schema.get("properties", {})
	required = schema.get("required", [])
	params = {}
	for param_name, param_schema in props.items():
		param_type = resolve_schema_type(param_schema)
		param_desc = param_schema.get("description", "")
		params[param_name] = {
			"type": param_type,
			"description": param_desc,
			"required": param_name in required
		}
	return params


def generate_signature(class_name: str, params: Dict[str, Any]) -> str:
	args = ", ".join(f"{name}: {meta['type']}" for name, meta in params.items())
	return f"{class_name}({args}) -> str"


def generate_example(class_name: str, params: Dict[str, Any]) -> str:
	args = ", ".join(f'"example_{name}"' if meta["type"].startswith("str") else "0" for name, meta in params.items())
	return f'{class_name}({args})'




def parse_response_examples(responses: Dict[str, Any]) -> List[str]:
    """
    Parses OpenAPI response definitions and extracts example responses.
    Supports complex outputs including objects and maps (additionalProperties).
    Returns a list of JSON strings.
    """
    examples = []

    for status_code, response in responses.items():
        content = response.get("content", {})
        app_json = content.get("application/json", {})
        schema = app_json.get("schema", {})

        # Prefer explicit example if present
        if "example" in app_json:
            example_data = app_json["example"]
        elif "examples" in app_json:
            # Multiple named examples (take the first one)
            example_values = list(app_json["examples"].values())
            if example_values:
                example_data = example_values[0].get("value")
            else:
                example_data = None
        else:
            # Build an example from schema if possible
            example_data = construct_example_from_schema(schema)

        if example_data is not None:
            try:
                examples.append(json.dumps(example_data))
            except Exception:
                examples.append(str(example_data))

    return examples


def construct_example_from_schema(schema: Dict[str, Any]) -> Any:
    """
    Recursively constructs a mock example based on a JSON schema.
    """
    schema_type = schema.get("type")

    if schema_type == "object":
        properties = schema.get("properties", {})
        if "additionalProperties" in schema:
            # This is a map/dictionary structure
            value_schema = schema["additionalProperties"]
            return {
                "example_key": construct_example_from_schema(value_schema)
            }
        return {
            key: construct_example_from_schema(value)
            for key, value in properties.items()
        }

    elif schema_type == "array":
        item_schema = schema.get("items", {})
        return [construct_example_from_schema(item_schema)]

    elif schema_type == "string":
        return schema.get("example", "example_string")

    elif schema_type == "integer":
        return schema.get("example", 42)

    elif schema_type == "number":
        return schema.get("example", 3.14)

    elif schema_type == "boolean":
        return schema.get("example", True)

    elif "anyOf" in schema:
        return construct_example_from_schema(schema["anyOf"][0])

    elif "oneOf" in schema:
        return construct_example_from_schema(schema["oneOf"][0])

    # Fallback for unknown or unsupported types
    return "example_value"



def format_operation(path: str, method: str, operation: Dict[str, Any]) -> Dict[str, Any]:
	operation_id = operation.get("operationId", f"{method}_{path.strip('/').replace('/', '_')}")
	class_name = operation_id#"".join(part.capitalize() for part in re.split(r"[\W_]+", operation_id))
	description = operation.get("description", "")
	request_body = operation.get("requestBody", {})
	params = parse_request_body(request_body) if request_body else {}
	signature = generate_signature(class_name, params)
	example = generate_example(class_name, params)
	output_examples = parse_response_examples(operation.get("responses", {}))
	
	return {
		"name": class_name,
		"signature": signature,
		"description": description,
		"params": params,
		"examples": [example],
		"output_examples": output_examples
	}


def summarize_oas_operations(oas: Dict[str, Any]) -> List[Dict[str, Any]]:
	operations = {}
	for path, methods in oas.get("paths", {}).items():
		for method, operation in methods.items():
			op = format_operation(path, method, operation)
			operations[op["name"]] = op
	return operations


# === Example usage ===
if __name__ == "__main__":
	oas_file = "/Users/naamazwerdling/Documents/OASB/policy_validation/airline/oas2.json"
	#oas_file = "/Users/naamazwerdling/Documents/OASB/policy_validation/airline/airline.json"
	#oas_file = "/Users/naamazwerdling/Documents/OASB/policy_validation/orca/bank/oas.json"
	with open(oas_file, "r") as f:
		openapi_spec = json.load(f)
		
	shortfile = "/Users/naamazwerdling/Documents/OASB/policy_validation/airline/short2.json"
	
	summaries = summarize_oas_operations(openapi_spec)
	print(json.dumps(summaries, indent=2))
	orig_oas_len = len(json.dumps(openapi_spec, indent=2))
	new_len = len(json.dumps(summaries, indent=2))
	print(f"Orig: {orig_oas_len}\tNew: {new_len}\tP: {orig_oas_len/new_len}")
	with open(shortfile, "w") as outfile:
		json.dump(summaries, outfile, indent=4)
