

import ast
import json
from typing import List

import astor
import yaml
from policy_adherence.tools.datamodel_codegen import run as dm_codegen
from policy_adherence.common.open_api import OpenAPI, Operation, Parameter, Schema

def read_oas(file_path:str)->OpenAPI:
    with open(file_path, "r") as file:
        if file_path.endswith("json"):
            d = json.load(file)
        else:
            d = yaml.safe_load(file)
    return OpenAPI.model_validate(d, strict=False)

primitive_oas_types_to_py = {
    "string": "str",
    "number": "float",
    "integer": "int",
    "boolean": "bool"
}
class OpenAPICodeGenerator():
    def generate_domain(self, oas_file:str, domain_py_file:str):
        dm_codegen(oas_file, domain_py_file)
        self.append_functions(domain_py_file, oas_file)

    def append_functions(self, domain_py_file:str, oas_file:str):
        oas = read_oas(oas_file)
        with open(domain_py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=domain_py_file)
        
        new_body = []
        new_body.append(ast.ImportFrom(
            module="typing",
            names=[
                ast.alias(name="Any", asname=None),
                ast.alias(name="Dict", asname=None),
                ast.alias(name="List", asname=None)
            ], 
            level=0 
        ))

        for path, path_item in oas.paths.items():
            for mtd, op in path_item.operations.items():
                params = (path_item.parameters or []) + (op.parameters or [])
                function_def = self.make_fn(op, params, oas)
                new_body.append(function_def)
        
        module = ast.Module(body=new_body, type_ignores=[])
        ast.fix_missing_locations(module)
        src= astor.to_source(module)
        with open(domain_py_file, "a", encoding="utf-8") as f:
            f.write(src)

    def make_fn(self, op: Operation, params: List[Parameter], oas:OpenAPI)->ast.FunctionDef:
        function_name = op.operationId
        args = [self.make_arg(param, oas) for param in params]
        if op.requestBody:
            scm = op.requestBody.content_json.schema_
            body_type = self.map_oas_to_py_type(scm)
            args.append(ast.arg(
                arg="request", 
                annotation=ast.Name(id=body_type, ctx=ast.Load())
            ))

        return_type = None
        rsp = op.responses.get("200")
        if rsp:
            scm = rsp.content_json.schema_
            if scm:
                type = self.map_oas_to_py_type(scm)
                return_type = ast.Name(id=type, ctx=ast.Load())

        fn = ast.FunctionDef(
            name=function_name,
            args=ast.arguments(
                args=args,  # Normal arguments
                posonlyargs=[],  # No positional-only arguments
                vararg=None,  # No *args
                kwonlyargs=[],  # No keyword-only arguments
                kw_defaults=[],  # No keyword defaults
                defaults=[]  # No default values
            ),
            body=[ast.Pass()],  # Empty function body (for now)
            decorator_list=[],  # No decorators
            returns=return_type  # Return type annotation
        ) # type: ignore
        
        doc = ast.Expr(value=ast.Constant(op.description))
        fn.body.insert(0, doc)
        return fn
    
    def map_oas_to_py_type(self, scm:Schema)->str:
        py_type = primitive_oas_types_to_py.get(scm.type)
        if py_type:
            return py_type
        if scm.ref:
            return scm.ref.split("/")[-1]
        if scm.type == "array":
            return f"List[{self.map_oas_to_py_type(scm.items)}]"
        return "Any"
    
    def make_arg(self, param: Parameter, oas:OpenAPI):
        py_type = self.map_oas_to_py_type(param.schema_)
        return ast.arg(
            arg=param.name, 
            annotation=ast.Name(id=py_type, ctx=ast.Load()))