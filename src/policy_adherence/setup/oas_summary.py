import json
import re
from typing import Any, Dict, List, Union


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
	return f"{class_name}.invoke(data: Dict[str, Any], {args}) -> str"


def generate_example(class_name: str, params: Dict[str, Any]) -> str:
	args = ", ".join(f'"example_{name}"' if meta["type"].startswith("str") else "0" for name, meta in params.items())
	return f'{class_name}.invoke(data, {args})'


def parse_response_examples(responses: Dict[str, Any]) -> List[str]:
	for status, resp in responses.items():
		if "content" in resp:
			schema = resp["content"].get("application/json", {}).get("schema", {})
			if "type" in schema and schema["type"] == "boolean":
				return ["true", "false"]
			elif "example" in schema:
				return [json.dumps(schema["example"])]
	return []


def format_operation(path: str, method: str, operation: Dict[str, Any]) -> Dict[str, Any]:
	operation_id = operation.get("operationId", f"{method}_{path.strip('/').replace('/', '_')}")
	class_name = "".join(part.capitalize() for part in re.split(r"[\W_]+", operation_id))
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
	operations = []
	for path, methods in oas.get("paths", {}).items():
		for method, operation in methods.items():
			operations.append(format_operation(path, method, operation))
	return operations


# === Example usage ===
if __name__ == "__main__":
	oas_file = "/Users/naamazwerdling/Documents/OASB/policy_validation/airline/oas2.json"
	#oas_file = "/Users/naamazwerdling/Documents/OASB/policy_validation/airline/airline.json"
	#oas_file = "/Users/naamazwerdling/Documents/OASB/policy_validation/orca/bank/oas.json"
	with open(oas_file, "r") as f:
		openapi_spec = json.load(f)
	
	summaries = summarize_oas_operations(openapi_spec)
	print(json.dumps(summaries, indent=2))
	orig_oas_len = len(json.dumps(openapi_spec, indent=2))
	new_len = len(json.dumps(summaries, indent=2))
	print(f"Orig: {orig_oas_len}\tNew: {new_len}\tP: {orig_oas_len/new_len}")
