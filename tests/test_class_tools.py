import asyncio
import inspect
import shutil
import unittest



from examples.calculator.end2end import ToolGuardFullFlow
from examples.calculator.inputs.class_tools import CalculatorTools
from toolguard.tool_policy_extractor.text_tool_policy_generator import extract_functions


class CalculatorTestClassTools(unittest.TestCase):
    def test_calculator_class_of_tools(self):
        wiki_path = "examples/calculator/inputs/policy_doc.md"
        work_dir = "examples/calculator/outputs/class_of_tools"
        
        # callable
        tools_class = CalculatorTools
        tools = [member for name, member in inspect.getmembers(tools_class, predicate=inspect.isfunction)]
      
        shutil.rmtree(work_dir, ignore_errors=True);
        tgb = ToolGuardFullFlow(wiki_path, work_dir, tools, app_name="calculator")
        asyncio.run(tgb.build_toolguards())
        fail = tgb.guard_tool_pass("divide_tool", {"g": 5, "h": 0})
        self.assertEqual(fail, False)
        success = tgb.guard_tool_pass("divide_tool", {"g": 5, "h": 4})
        self.assertEqual(success, True)


if __name__ == '__main__':
	unittest.main()
