import os
from os.path import join
from typing import Callable, List, Optional, Any, Dict
import json
import logging

from langchain.tools import BaseTool
from pydantic import BaseModel

from toolguard.common.open_api import OpenAPI

from .llm.i_tg_llm import I_TG_LLM
from .runtime import ToolGuardsCodeGenerationResult
from .data_types import ToolPolicy, load_tool_policy, ToolInfo
from .gen_py.gen_toolguards import generate_toolguards_from_functions, generate_toolguards_from_openapi
from .gen_spec.oas_summary import OASSummarizer
from .gen_spec.spec_generator import extract_policies

logger = logging.getLogger(__name__)

async def build_toolguards(
		policy_text:str, 
		tools: List[Callable]|str, 
		step1_out_dir:str, 
		step2_out_dir:str, 
		step1_llm:I_TG_LLM, 
		app_name:str= "my_app", 
		tools2run: List[str] | None=None, 
		short1=True)->ToolGuardsCodeGenerationResult:
	os.makedirs(step1_out_dir, exist_ok=True)
	os.makedirs(step2_out_dir, exist_ok=True)

	# case1: path to OpenAPI spec
	oas_path = tools if isinstance(tools, str) else None

	# case2: List of Langchain tools
	if isinstance(tools, list) and all([isinstance(tool, BaseTool) for tool in tools]):
		oas =_langchain_tools_to_openapi(tools) # type: ignore
		oas_path = f"{step1_out_dir}/oas.json"
		oas.save(oas_path)

	if oas_path: # for cases 1 and 2
		with open(oas_path, 'r', encoding='utf-8') as file:
			oas = json.load(file)
		summarizer = OASSummarizer(oas)
		tools_info = summarizer.summarize()
		tool_policies = await extract_policies(policy_text, tools_info, step1_out_dir, step1_llm, tools2run, short1)
		return await generate_guards_from_tool_policies_oas(oas_path, tool_policies, step2_out_dir, app_name, tools2run)
	
	# Case 3: List of functions + case 4: List of methods
	if isinstance(tools, list) and not oas_path:
		tools_info = [ToolInfo.from_function(tool) for tool in tools]
		tool_policies = await extract_policies(policy_text, tools_info, step1_out_dir, step1_llm, tools2run, short1)
		return await generate_guards_from_tool_policies(tools, tool_policies, step2_out_dir, app_name, None, tools2run)
	
	raise Exception("Unknown tools")


async def generate_guards_from_tool_policies(
		funcs: List[Callable],
		tool_policies: List[ToolPolicy],
		step2_path: str,
		app_name: str,
		lib_names: Optional[List[str]] = None,
		tool_names: Optional[List[str]] = None) -> ToolGuardsCodeGenerationResult:
	
	tool_policies = [policy for policy in tool_policies if (not tool_names) or (policy.tool_name in tool_names)]
	return await generate_toolguards_from_functions(app_name, tool_policies, step2_path, funcs=funcs, module_roots=lib_names)


async def generate_guards_from_tool_policies_oas(
		oas_path: str,
		tool_policies: List[ToolPolicy],
		to_step2_path: str,
		app_name: str,
		tool_names: Optional[List[str]] = None) -> ToolGuardsCodeGenerationResult:
	
	tool_policies = [policy for policy in tool_policies if (not tool_names) or (policy.tool_name in tool_names)]
	return await generate_toolguards_from_openapi(app_name, tool_policies, to_step2_path, oas_path)


def load_policies_in_folder(folder:str)->List[ToolPolicy]:
	files = [f for f in os.listdir(folder) 
		if os.path.isfile(join(folder, f)) and f.endswith(".json")]
	tool_policies = []
	for file in files:
		tool_name = file[:-len(".json")]
		policy = load_tool_policy(join(folder, file), tool_name)
		if policy.policy_items:
			tool_policies.append(policy)
	return tool_policies


def _langchain_tools_to_openapi(
    tools: List[BaseTool],
    title: str = "LangChain Tools API",
    version: str = "1.0.0",
)->OpenAPI:
    paths = {}
    components = {"schemas": {}}

    for tool in tools:
        # Get JSON schema from the args model
        if hasattr(tool, "args_schema") and issubclass(tool.args_schema, BaseModel):
            schema = tool.args_schema.model_json_schema()
            components["schemas"][tool.name + "Args"] = schema

            request_body = {
                "description": tool.description,
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{tool.name}Args"}
                    }
                },
            }
        else:
            # Tools without args → empty schema
            request_body = None

        paths[f"/tools/{tool.name}"] = {
            "post": {
                "summary": tool.description,
                "operationId": tool.name,
                "requestBody": request_body,
                "responses": {
                    "200": {
                        "description": "Tool result",
                        "content": {"application/json": {}},
                    }
                },
            }
        }

    return OpenAPI.model_validate({
        "openapi": "3.1.0",
        "info": {"title": title, "version": version},
        "paths": paths,
        "components": components,
    })
