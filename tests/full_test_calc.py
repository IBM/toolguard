import asyncio
import os
from typing import List, Dict

import dotenv
import markdown

from tests.calculator.tools import divide_tool
# from toolguard import build_toolguards
from toolguard.llm.tg_litellm import LitellmModel
from toolguard.stages_tptd.text_tool_policy_generator import ToolInfo, step1_main
from toolguard.core import generate_guards_from_tool_policies



class FullAgent:
	def __init__(self, app_name, tools, workdir, policy_doc_path, llm_model="gpt-4o-2024-08-06",
				 tools2run: List[str] | None = None, short1=False):
		self.model = llm_model
		self.tools = tools
		self.workdir = workdir
		self.policy_doc = open(policy_doc_path, 'r', encoding='utf-8').read()
		self.policy_doc = markdown.markdown(self.policy_doc)
		self.tools2run = tools2run
		self.short1 = short1
		self.app_name = app_name
		self.step1_out_dir = os.path.join(self.workdir, "step1")
		self.step2_out_dir = os.path.join(self.workdir, "step2")
		#self.tool_registry = {tool.name: tool for tool in tools}
		self.tool_registry = {tool.__name__: tool for tool in tools}

	
	async def build_time(self):
		llm = LitellmModel(model_name=self.model, provider="azure")
		tools_info = [ToolInfo.from_function(tool) for tool in self.tools]
		
		await step1_main(self.policy_doc, tools_info, self.step1_out_dir, llm, short=True)
		await generate_guards_from_tool_policies(self.tools, from_step1_path=self.step1_out_dir, to_step2_path=self.step2_out_dir,
												 app_name=self.app_name)
	
	def guard_tool_pass(self, tool_name:str,tool_params:Dict) -> bool:
		print("validate_tool_node")
		import sys
		sys.path.insert(0, self.step2_out_dir)
		from rt_toolguard import load_toolguards
		toolguards = load_toolguards(self.step2_out_dir)
		from rt_toolguard.data_types import PolicyViolationException

		try:
			# app_guards.check_tool_call(tool_name, tool_parms, state["messages"])
			toolguards.check_toolcall(tool_name, tool_params, list(self.tool_registry.values()))
			print("ok to invoke tool")
			return True
		except Exception as e:
			error_message = "it is against the policy to invoke tool: " + tool_name + " Error: " + str(e)
			print(error_message)
			return False



