import asyncio
import os
import unittest
import dotenv
from dotenv import load_dotenv

from tests.calculator.tools import divide_tool, add_tool, subtract_tool, multiply_tool
from tests.full_test_calc import FullAgent


class CalculatorTestCase(unittest.TestCase):
    def test_calculator(self):
        file_path = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_path)
        parent_dir = os.path.dirname(dir_path)
        env_path = os.path.join(parent_dir, ".env")
        load_dotenv(env_path)
        work_dir = os.path.join(dir_path,"output")
        os.makedirs(work_dir, exist_ok=True)
        policy_doc_path = os.path.join(dir_path,"policy_doc.md")
        
        tools = [add_tool, subtract_tool, multiply_tool, divide_tool]
        fa = FullAgent("calculator", tools, work_dir, policy_doc_path, llm_model="gpt-4o-2024-08-06", short1=True)
        asyncio.run(fa.build_time())
        fail = fa.guard_tool_pass("divide_tool", {"g": 5, "h": 0})
        self.assertEqual(fail, False)
        success = fa.guard_tool_pass("divide_tool", {"g": 5, "h": 4})
        self.assertEqual(success, True)


if __name__ == '__main__':
	unittest.main()
