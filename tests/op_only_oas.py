
from policy_adherence.common.dict import substitute_refs
from policy_adherence.common.open_api import *


def op_only_oas(oas: OpenAPI, operationId: str)-> OpenAPI:
    new_oas = OpenAPI(
        openapi=oas.openapi, 
        info=oas.info,
        # components=oas.components
    )
    for path, path_item in oas.paths.items():
            path_item = oas.resolve_ref(path_item, PathItem)
            for mtd, op in path_item.operations.items():
                op = oas.resolve_ref(op, Operation)
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
                        Operation(**(substitute_refs(op.model_dump(by_alias=True), oas.model_dump(by_alias=True))))
                    )
    return new_oas

def read_oas(file_path:str)->OpenAPI:
    with open(file_path, "r") as file:
        d = yaml.safe_load(file)
    return OpenAPI.model_validate(d)

if __name__ == '__main__':
     oas_path = "/Users/davidboaz/Documents/GitHub/tau_airline/input/openapi.yaml"
     oas = read_oas(oas_path)
     op_oas = op_only_oas(oas, "book_reservation")
     print(op_oas.model_dump_json(indent=2, exclude_none=True, by_alias=True))