

from typing import List, Tuple
from loguru import logger

from policy_adherence.llm.llm_model import LLM_model
from policy_adherence.utils import call_llm, extract_code_from_llm_response
from policy_adherence.types import Code, ToolPolicy, ToolPolicyItem
from policy_adherence.tools.pyright import run_pyright
from policy_adherence.tools.pytest import run_unittests

class ToolPolicyTestsGenerator:
    llm: LLM_model
    cwd: str

    def __init__(self, llm:LLM_model, cwd:str) -> None:
        self.llm = llm
        self.cwd = cwd

    def generate_tool_tests(self, fn_under_test:Code, tool:ToolPolicy, retries=2)-> Tuple[Code, List[str]]:
            logger.debug(f"Generating Tests... (retries={retries})")
            # TODO domain
            prompt = f"""You are given a function stub in Python. This function is under test:
```
### {fn_under_test.file_name}
{fn_under_test.content}
```
make sure to import it from {fn_under_test.file_name}.

You are also given with policy statements that the function under test should comply with.
For each statement, you are also provided with positive and negative examples.

Your task is to write unit tests to check that the function implementation check the policy statements.
Generate one test for each policy statement example.
For negative examples, check that the funtion under test raise a `builtins.Exception`.
For positive cases check that no exception raised.
Indicate test failures using a meaningful message that also contain the policy statement and the example.

{tool.policies_to_md()}
    """
            res_content = call_llm(prompt, self.llm)
            body = extract_code_from_llm_response(res_content)
            
            tests = Code(file_name=f"test_check_{tool.name}.py", content=body)
            tests.save(self.cwd)
            lint_report = run_pyright(self.cwd, tests.file_name)
            if lint_report.list_errors():
                logger.warning(f"Generated tests with Python errors.")
                if retries>0:
                    return self.generate_tool_tests(fn_under_test, tool, retries=retries-1)
                raise Exception("Generated tests contain errors")
        
            #syntax ok, try to run it...
            logger.debug(f"Generated Tests... (retries={retries})")
            #still running against a stub. the tests should fail, but the collector should not fail.
            test_report = run_unittests(self.cwd)
            if not test_report.all_tests_collected_successfully():
                logger.debug(f"Tool {tool.name} unit tests error")
                return self.generate_tool_tests(fn_under_test, tool, retries=retries-1)
            
            return tests, test_report.list_errors()
