import importlib
import inspect
from pathlib import Path
import types
import sys
from typing import Any, Dict, Literal, Set, Type, List, Union, Any, Callable, Dict, List, Set, Tuple, Union, get_type_hints, Type
import re

def extract_api_methods(cls: Type) -> Dict[str, Dict[str, Any]]:
    """Extract public method names, their signatures, and type hints."""
    api_methods: Dict[str, Dict[str, Any]] = {}
    for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        sig = inspect.signature(func)
        try:
            hints = get_type_hints(func, globalns=globals(), localns=vars(cls))
        except Exception:
            hints = {}
        api_methods[name] = {"signature": sig, "annotations": hints}
    return api_methods


def _extract_all_potential_aliases_from_source(source_path: Path) -> Dict[str, str]:
    """
    Extracts all top-level assignments from the source file that could be type aliases.
    Returns a dictionary of {alias_name: full_definition_string}.
    """
    src = source_path.read_text()
    lines = src.splitlines()
    potential_aliases: Dict[str, str] = {}
    current_block_lines: List[str] = []
    current_name: Union[str, None] = None
    bracket_level = 0
    assign_re = re.compile(r"^\s*(\w+)\s*=")

    i = 0
    while i < len(lines):
        line = lines[i]
        m = assign_re.match(line)
        if m:
            name = m.group(1)
            # Start of a new potential alias definition
            current_name = name
            current_block_lines = [line.strip()] # Store the whole line
            bracket_level = line.count("[") + line.count("(") + line.count("{") - line.count("]") - line.count(")") - line.count("}")
            if bracket_level <= 0: # Single line alias
                potential_aliases[current_name] = current_block_lines[0]
                current_name = None
                current_block_lines = []
            i += 1
            continue
        elif current_name:
            # Continuation of a multi-line alias
            current_block_lines.append(line.strip())
            bracket_level += line.count("[") + line.count("(") + line.count("{")
            bracket_level -= line.count("]") + line.count(")") + line.count("}")
            if bracket_level <= 0:
                potential_aliases[current_name] = "\n".join(current_block_lines)
                current_name = None
                current_block_lines = []
            i += 1
            continue
        i += 1
    
    potential_aliases ={alias: re.sub(r'^\s*\w+\s*=\s*', '', potential_aliases[alias]) for alias in potential_aliases if alias[0].isupper()}

    return potential_aliases

def get_all_dependent_types(cls: Type, collected: Set[Type], module_prefix="tau2.") -> None:
    """Recursively collect cls, its base classes, and nested types from annotations."""
    if cls in collected:
        return
    if cls.__module__ == "builtins":
        return

    collected.add(cls)

    # Bases
    for base in cls.__bases__:
        if hasattr(base, "__module__") and base.__module__.startswith(module_prefix):
            get_all_dependent_types(base, collected, module_prefix)

    # Skip enum details
    import enum
    if issubclass(cls, enum.Enum):
        return

    # Annotations
    try:
        hints = inspect.get_annotations(cls, globals(), locals())
    except Exception:
        hints = getattr(cls, "__annotations__", {})

    for field_type in hints.values():
        collect_nested_type(field_type, collected, module_prefix)

def collect_nested_type(t: Any, collected: Set[Type], module_prefix="tau2.") -> None:
    """Recursively collect types from type hint t."""
    if t is None:
        return
    if isinstance(t, types.UnionType):
        for arg in t.__args__:
            collect_nested_type(arg, collected, module_prefix)
        return
    origin = getattr(t, "__origin__", None)
    if origin is Union:
        for arg in t.__args__:
            collect_nested_type(arg, collected, module_prefix)
        return
    if origin in {list, List, tuple, Tuple, set, Set}:
        for arg in getattr(t, "__args__", ()):
            collect_nested_type(arg, collected, module_prefix)
        return
    if isinstance(t, type) and t.__module__.startswith(module_prefix):
        get_all_dependent_types(t, collected, module_prefix)

def get_used_types_with_bases_and_fields(api_methods: Dict[str, Dict[str, Any]], module_prefix="tau2.") -> Set[Type]:
    collected: Set[Type] = set()

    def collect(t: Any) -> None:
        if t is None:
            return
        if isinstance(t, types.UnionType):
            for arg in t.__args__:
                collect(arg)
        elif getattr(t, "__origin__", None) is Union:
            for arg in t.__args__:
                collect(arg)
        elif getattr(t, "__origin__", None) in {list, List}:
            for arg in t.__args__:
                collect(arg)
        elif isinstance(t, type) and t.__module__.startswith(module_prefix):
            get_all_dependent_types(t, collected, module_prefix)

    for method in api_methods.values():
        for k,t in method["annotations"].items():
            collect(t)

    return collected

def generate_types_file_with_classes_and_aliases(
    api_methods: Dict[str, Dict[str, Any]],
    output_path: Path,
    data_model_module_name: str = "tau2.domains.airline.data_model",
) -> None:
    spec = importlib.util.find_spec(data_model_module_name)
    source_path = Path(spec.origin)
    aliases = _extract_all_potential_aliases_from_source(source_path)

    # Step 1: Collect all used classes recursively
    module_prefix = data_model_module_name.split(".")[0]
    used_classes = get_used_types_with_bases_and_fields(api_methods, module_prefix)

    def inheritance_depth(cls: Type) -> int:
        if cls is object:
            return 0
        depth = 0
        for base in cls.__bases__:
            if base is object:
                continue
            depth = max(depth, inheritance_depth(base) + 1)
        return depth

    sorted_classes = sorted(used_classes, key=inheritance_depth)

    class_sources = []
    for cls in sorted_classes:
        try:
            src = inspect.getsource(cls).strip()
            new_src = src
            for alias, val in aliases.items():
                new_src = re.sub(rf'\b{re.escape(alias)}\b', val, new_src)
            class_sources.append(new_src)
        except (OSError, TypeError):
            print(f"Warning: Could not get source for class {cls.__name__}")

    # Step 6: Write combined output
    lines = [
        "# AUTO-GENERATED TYPE DEFINITIONS API",
        "from __future__ import annotations",
        "from typing import *",
        "from enum import Enum",
        "from pydantic import BaseModel, Field",
        "",
        # alias_source_code,
        "",
    ]
    lines.extend(class_sources)

    output_path.write_text("\n\n".join(lines))

def format_type(t: Any) -> str:
    """Convert a type hint to a human-readable string with clean names for tau2 types."""
    # Handle None specifically
    if t is None:
        return "None"

    # Check for union types created with the | operator (PEP 604)
    if isinstance(t, types.UnionType):
        args = t.__args__
        # Format each argument and join with the union symbol
        return " | ".join(sorted(set(format_type(arg) for arg in args)))

    # For traditional typing.Union (if any)
    origin = getattr(t, '__origin__', None)
    if origin is Union:
        args = getattr(t, '__args__', ())
        return " | ".join(sorted(set(format_type(arg) for arg in args)))

    # Handle list types
    if origin in {list, List}:
        return f"List[{format_type(t.__args__[0])}]"

    # For types that have a __name__, use it (if the type is defined in tau2, show only the class name)
    if hasattr(t, '__name__'):
        if hasattr(t, '__module__') and t.__module__.startswith("tau2."):
            return t.__name__
        return t.__name__

    # Fallback to a simple string conversion, removing the "typing." prefix if present.
    return str(t).replace("typing.", "")

def generate_interface_file(api_methods: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    """Generate the airline_api_interface.py file with an abstract base class."""
    lines: List[str] = [
        "from abc import ABC, abstractmethod",
        "from typing import *",
        "from airline_api_types import *",
        "",
        "class AirlineAPI(ABC):"
    ]

    for method_name, info in api_methods.items():
        sig = info["signature"]
        hints = info["annotations"]

        args: List[str] = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            ann: str = format_type(hints.get(name, Any))
            default: str = f" = {repr(param.default)}" if param.default != param.empty else ""
            args.append(f"{name}: {ann}{default}")

        return_type: str = format_type(hints.get("return", Any))
        method_signature: str = f"@abstractmethod\n    def {method_name}(self, {', '.join(args)}) -> {return_type}: ..."
        lines.append("")
        lines.append(f"    {method_signature}")

    with output_path.open("w") as f:
        f.write("\n".join(lines))

def parse_type_string_for_dependencies_recursive(type_string: str,
                                               collected_classes: Set[Type],
                                               collected_alias_names: Set[str],
                                               all_potential_aliases: Dict[str, str],
                                               module_prefix: str,
                                               seen_strings: Set[str]):
    """
    Recursively parses a type string to find dependent types (classes and aliases).
    Adds found classes to collected_classes and found alias names to collected_alias_names.
    'seen_strings' prevents infinite recursion for circular dependencies.
    """
    if type_string in seen_strings:
        return
    seen_strings.add(type_string)

    # Simplified parsing: find words that could be type names
    # This is a heuristic and might need to be more sophisticated for complex cases
    potential_names = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', type_string)

    for name in potential_names:
        # Skip common built-ins or typing module names that don't need explicit collection
        if name in {"List", "Dict", "Set", "Tuple", "Union", "Any", "Callable", "Optional", "None"}:
            continue

        # Try to resolve the name to an actual type object if it's already loaded
        # This is best effort and relies on types being globally available or imported
        try:
            # We need a context for eval. For simplicity, using current globals.
            # A more robust solution would involve symbol table management.
            resolved_type = eval(name, globals(), sys.modules[module_prefix.split('.')[0]].__dict__)
            
            if isinstance(resolved_type, type):
                # If it's a class and from our target module prefix
                if resolved_type.__module__.startswith(module_prefix):
                    get_all_dependent_types(resolved_type, collected_classes, module_prefix)
            elif isinstance(resolved_type, (types.UnionType, type(Union))): # Union types
                for arg in getattr(resolved_type, '__args__', ()):
                    collect_nested_type(arg, collected_classes, module_prefix)
            # Add more specific type handling (e.g., if you have custom type objects)

        except (NameError, TypeError):
            # If resolution failed, it might be a type alias not yet resolved or a forward reference
            if name in all_potential_aliases and name not in collected_alias_names:
                collected_alias_names.add(name)
                # Recursively parse the alias's definition string
                parse_type_string_for_dependencies_recursive(
                    all_potential_aliases[name],
                    collected_classes,
                    collected_alias_names,
                    all_potential_aliases,
                    module_prefix,
                    seen_strings
                )

def main() -> None:
    """Main function to extract API and generate output files."""
    from tau2.domains.airline.tools import AirlineTools  # Replace with the actual import
    api_methods: Dict[str, Dict[str, Any]] = extract_api_methods(AirlineTools)
    output_dir: Path = Path(".")

    generate_types_file_with_classes_and_aliases(api_methods, output_dir / "airline_api_types.py")
    generate_interface_file(api_methods, output_dir / "airline_api_interface.py")


if __name__ == "__main__":
    main()
