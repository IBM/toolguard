import inspect
from types import FunctionType
from typing import Dict, List, Literal, Set, Tuple, get_type_hints, get_origin, get_args
from typing import Annotated, Union
from pathlib import Path
from collections import defaultdict, deque
import typing

class TypeExtractor:
    def __init__(self):
        self.module_roots: List[str] = []
        self.collected_types: Set[type]= set()
        self.type_definitions = {}
        self.imports = set()
        self.processed_types: Set[type] = set()
        self.type_dependencies = defaultdict(set)  # type -> set of types it depends on
        self.literal_values = {}  # Store literal type values
        
    def extract_from_class(self, typ:type, output_dir="output")->Tuple[str, str]:
        """Extract interface and types from a class and save to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        class_name = _get_type_name(typ)
        
        self.module_roots = [typ.__module__.split(".")[0]] #ex: "tau2". 

        # Extract interface
        interface_content = self._generate_interface(typ)
        
        # Extract all required types
        self._collect_all_types_from_class(typ)
        types_content = self._generate_types_file()
        
        # Save files
        interface_file = output_path / f"{class_name.lower()}_interface.py"
        types_file = output_path / f"{class_name.lower()}_types.py"
        
        with open(interface_file, 'w') as f:
            f.write(interface_content)
            
        with open(types_file, 'w') as f:
            f.write(types_content)
            
        print(f"Generated {interface_file}")
        print(f"Generated {types_file}")
        
        return str(interface_file), str(types_file)
    
    def _generate_interface(self, typ:type)->str:
        """Generate the interface file content."""
        class_name = _get_type_name(type)
        
        # Get type hints for the class
        try:
            type_hints = get_type_hints(typ)
        except:
            type_hints = {}
        
        # Start building the interface
        lines = []
        lines.append("# Auto-generated class interface")
        lines.append("from typing import *")
        lines.append("from abc import ABC, abstractmethod")
        lines.append(f"from {class_name.lower()}_types import *")
        lines.append("")
        
        # # Get base classes (excluding BaseModel and object)
        # bases = []
        # for base in _get_type_bases(typ):
        #     if base != object:
        #         bases.append(_get_type_name(base))
        
        lines.append(f"class {class_name}(ABC):") #Abstract class
        
        # Add class docstring if available
        if typ.__doc__:
            docstring = typ.__doc__.strip()
            if docstring:
                lines.append(f'    """')
                # Handle multi-line docstrings
                for line in docstring.split('\n'):
                    lines.append(f'    {line.strip()}')
                lines.append(f'    """')
        
        # Get all methods
        methods = []
        for name, method in inspect.getmembers(typ, predicate=inspect.isfunction):
            if not name.startswith('_'):
                methods.append((name, method))
        
        if not methods:
            lines.append("    pass")
        else:
            for method_name, method in methods:
                # Add method docstring and signature
                method_lines = self._get_method_with_docstring(method, method_name)
                lines.extend([line if line else "" for line in method_lines])
                lines.append("")
        
        return "\n".join(lines)
    
    def _get_method_with_docstring(self, method:FunctionType, method_name:str)->List[str]:
        """Extract method signature with type hints and docstring."""
        lines = ["    @abstractmethod"]
        
        # Get method signature
        method_signature = self._get_method_signature(method, method_name)
        lines.append(f"    {method_signature}:")
        
        # Add method docstring if available
        if method.__doc__:
            docstring = method.__doc__.strip()
            if docstring:
                lines.append('        """')
                for line in docstring.split('\n'):
                    lines.append(f'        {line.strip()}')
                lines.append('        """')
        
        lines.append("        ...")
        
        return lines
    
    def should_include_type(self, typ:type)->bool:
        if hasattr(typ, '__module__'):
            module_root = typ.__module__.split(".")[0]
            if module_root in self.module_roots:
                return True
        return any([self.should_include_type(arg) for arg in get_args(typ)])

    def _generate_class_definition(self, typ:type) -> List[str]:
        """Generate a class definition with its fields."""
        lines = []
        class_name = _get_type_name(typ)
        
        # Determine base classes
        bases = [_get_type_name(b) for b in _get_type_bases(typ)]
        inheritance = f"({', '.join(bases)})" if bases else ""
        lines.append(f"class {class_name}{inheritance}:")
        
        # #is Pydantic?
        # is_pydantic = False
        # for base in cls.__bases__:
        #     if hasattr(base, '__module__') and 'pydantic' in str(base.__module__):
        #         is_pydantic = True

        # Add class docstring if available
        if typ.__doc__:
            docstring = typ.__doc__.strip()
            if docstring:
                lines.append(f'    """')
                # Handle multi-line docstrings
                for line in docstring.split('\n'):
                    lines.append(f'    {line.strip()}')
                lines.append(f'    """')
        
        annotations = getattr(typ, '__annotations__', {})
        field_descriptions = self._extract_field_descriptions(typ)
        
        #Fields
        if annotations:
            for field_name, field_type in annotations.items():
                if field_name.startswith('_'):
                    continue
                
                # Handle optional field detection by default=None
                is_optional = False
                default_val = getattr(typ, field_name, ...)
                if default_val is None:
                    is_optional = True
                elif hasattr(typ, '__fields__'):
                    # Pydantic field with default=None
                    field_info = typ.__fields__.get(field_name)
                    if field_info and field_info.is_required() is False:
                        is_optional = True

                type_str = self._format_type(field_type)

                # Avoid wrapping Optional twice
                if is_optional:
                    origin = get_origin(field_type)
                    args = get_args(field_type)
                    already_optional = (
                        origin is typing.Union and type(None) in args
                        or type_str.startswith("Optional[")
                    )
                    if not already_optional:
                        type_str = f"Optional[{type_str}]"
                
                # Check if we have a description for this field
                description = field_descriptions.get(field_name)
                
                # if description and is_pydantic:
                #     # Use Pydantic Field with description
                #     lines.append(f'    {field_name}: {type_str} = Field(description="{description}")')
                if description:
                    # Add description as comment for non-Pydantic classes
                    lines.append(f'    {field_name}: {type_str}  # {description}')
                else:
                    # No description available
                    lines.append(f'    {field_name}: {type_str}')
        else:
            lines.append("    pass")
        
        return lines
    
    def _extract_field_descriptions(self, typ:type)->Dict[str, str]:
        """Extract field descriptions from various sources."""
        descriptions = {}
        
        # Method 1: Check for Pydantic Field definitions
        if hasattr(typ, '__fields__'):  # Pydantic v1
            for field_name, field_info in typ.__fields__.items():
                if hasattr(field_info, 'field_info') and hasattr(field_info.field_info, 'description'):
                    descriptions[field_name] = field_info.field_info.description
                elif hasattr(field_info, 'description') and field_info.description:
                    descriptions[field_name] = field_info.description
        
        # Method 2: Check for Pydantic v2 model fields
        if hasattr(typ, 'model_fields'):  # Pydantic v2
            for field_name, field_info in typ.model_fields.items():
                if hasattr(field_info, 'description') and field_info.description:
                    descriptions[field_name] = field_info.description
        
        # Method 3: Check class attributes for Field() definitions
        for attr_name in dir(typ):
            if not attr_name.startswith('_'):
                try:
                    attr_value = getattr(typ, attr_name)
                    # Check if it's a Pydantic Field
                    if hasattr(attr_value, 'description') and attr_value.description:
                        descriptions[attr_name] = attr_value.description
                    elif hasattr(attr_value, 'field_info') and hasattr(attr_value.field_info, 'description'):
                        descriptions[attr_name] = attr_value.field_info.description
                except:
                    pass
        
        # Method 4: Parse class source for inline comments or docstrings
        try:
            source_lines = inspect.getsourcelines(typ)[0]
            current_field = None
            
            for line in source_lines:
                line = line.strip()
                
                # Look for field definitions with type hints
                if ':' in line and not line.startswith('def ') and not line.startswith('class '):
                    # Extract field name
                    field_part = line.split(':')[0].strip()
                    if ' ' not in field_part and field_part.isidentifier():
                        current_field = field_part
                
                # Look for comments on the same line or next line
                if '#' in line and current_field:
                    comment = line.split('#', 1)[1].strip()
                    if comment and current_field not in descriptions:
                        descriptions[current_field] = comment
                    current_field = None
                    
        except:
            pass
        
        # Method 5: Check for dataclass field descriptions
        if hasattr(typ, '__dataclass_fields__'):
            for field_name, field in typ.__dataclass_fields__.items():
                if hasattr(field, 'metadata') and 'description' in field.metadata:
                    descriptions[field_name] = field.metadata['description']
        
        return descriptions
    
    def _get_method_signature(self, method:FunctionType, method_name:str):
        """Extract method signature with type hints."""
        try:
            sig = inspect.signature(method)
            # Get param hints
            try:
                param_hints = get_type_hints(method)
            except:
                param_hints = {}
            
            params = []
            for param_name, param in sig.parameters.items():
                param_str = param_name
                
                # Add type annotation if available
                if param_name in param_hints:
                    type_str = self._format_type(param_hints[param_name])
                    param_str += f": {type_str}"
                elif param.annotation != param.empty:
                    param_str += f": {param.annotation}"
                
                # Add default value if present
                if param.default != param.empty:
                    if isinstance(param.default, str):
                        param_str += f' = "{param.default}"'
                    else:
                        param_str += f" = {repr(param.default)}"
                
                params.append(param_str)
            
            # Handle return type
            return_annotation = ""
            if 'return' in param_hints:
                return_type = self._format_type(param_hints['return'])
                return_annotation = f" -> {return_type}"
            elif sig.return_annotation != sig.empty:
                return_annotation = f" -> {sig.return_annotation}"
            
            params_str = ", ".join(params)
            return f"def {method_name}({params_str}){return_annotation}"
            
        except Exception as e:
            # Fallback for problematic signatures
            return f"def {method_name}(self, *args, **kwargs)"
    
    def _collect_all_types_from_class(self, typ:type):
        """Collect all types used in the class recursively."""

        # Field types
        try:
            class_hints = get_type_hints(typ)
            for field, hint in class_hints.items():
                self._collect_types_recursive(hint)
        except:
            pass
        
        # Methods and param types
        for name, method in inspect.getmembers(typ, predicate=inspect.isfunction):
            try:
                method_hints = get_type_hints(method)
                for hint in method_hints.values():
                    self._collect_types_recursive(hint)
            except:
                pass
        
        # Also collect base class types
        for base in _get_type_bases(typ):
            self._collect_types_recursive(base)
    
    def _collect_types_recursive(self, typ: type):
        """Recursively collect all types from a type hint."""
        
        if typ in self.processed_types:
            return
            
        self.processed_types.add(typ)
        
        if not self.should_include_type(typ):
            return

        origin = get_origin(typ)
        args = get_args(typ)

        #Type with generic arguments. eg: List[Person]
        if origin and args:
            self.collected_types.add(typ)
            for f_arg in args:
                self._collect_types_recursive(f_arg)
                self._add_dependency(typ, f_arg)
        
            # Handle Literal types specially
            if origin is typing.Literal or (hasattr(typing, '_LiteralGenericAlias') and 
                                         isinstance(typ, typing._LiteralGenericAlias)):
                self.collected_types.add(typ)
                # Store literal values
                self.literal_values[typ] = args
            
            return
        
        # Handle regular classes and custom types
        self.collected_types.add(typ)
        
        # If it's a custom class, try to get its type hints
        try:
            field_hints = typ.__annotations__ #direct fields
            for field_name, field_hint in field_hints.items():
                f_origin = get_origin(field_hint)
                if f_origin:
                    for f_arg in get_args(field_hint):
                        self._collect_types_recursive(f_arg)
                        self._add_dependency(typ, f_arg)
                else:
                    self._collect_types_recursive(field_hint)
                    self._add_dependency(typ, field_hint)

            for base in _get_type_bases(typ): #Base classes
                self._collect_types_recursive(base)
                self._add_dependency(typ, base)
        except:
            pass
    
    def _add_dependency(self, dependent_type, dependency_type):
        """Add a dependency relationship between types."""
        dep_name = _get_type_name(dependent_type)
        dep_on_name = _get_type_name(dependency_type)
        if dep_name != dep_on_name:
            self.type_dependencies[dependent_type].add(dependency_type)

    def _topological_sort_types(self, types):
        """Sort types by their dependencies using topological sort."""
        # Create a mapping of type names to types for easier lookup
        type_map = {_get_type_name(t): t for t in types}
        
        # Build adjacency list and in-degree count
        adj_list = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize in-degree for all types
        for t in types:
            type_name = _get_type_name(t)
            if type_name not in in_degree:
                in_degree[type_name] = 0
        
        # Build the dependency graph
        for dependent_type in types:
            dependent_name = _get_type_name(dependent_type)
            for dependency_type in self.type_dependencies.get(dependent_type, set()):
                dependency_name = _get_type_name(dependency_type)
                if dependency_name in type_map:  # Only consider types we're actually processing
                    adj_list[dependency_name].append(dependent_name)
                    in_degree[dependent_name] += 1
        
        # Kahn's algorithm for topological sorting
        queue = deque([name for name in in_degree if in_degree[name] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(type_map[current])
            
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we couldn't sort all types, there might be circular dependencies
        # Add remaining types at the end
        sorted_names = {_get_type_name(t) for t in result}
        remaining = [t for t in types if _get_type_name(t) not in sorted_names]
        result.extend(remaining)
        
        return result
    
    def _generate_types_file(self)->str:
        """Generate the types file content."""
        lines = []
        lines.append("# Auto-generated type definitions")
        lines.append("from enum import Enum")
        lines.append("from abc import ABC")
        lines.append("from typing import *")
        lines.append("from datetime import datetime, date")
        lines.append("from decimal import Decimal")
        lines.append("from uuid import UUID")
        lines.append("from pydantic import BaseModel, Field")
        lines.append("")
        
        custom_classes = []
        for typ in self.collected_types:
            # Check if it's a class with attributes
            if (hasattr(typ, '__annotations__') or 
                (hasattr(typ, '__dict__') and 
                 any(not callable(getattr(typ, attr, None)) 
                     for attr in dir(typ) if not attr.startswith('_')))):
                custom_classes.append(typ)
        custom_classes = self._topological_sort_types(custom_classes)
        
        # Generate custom classes (sorted by dependency)
        for cls in custom_classes:
            class_def = self._generate_class_definition(cls)
            if class_def:  # Only add non-empty class definitions
                lines.extend(class_def)
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_type(self, typ: type) -> str:
        if typ is None:
            return "Any"

        # Unwrap Annotated[T, ...]
        origin = get_origin(typ)
        if origin is Annotated:
            typ = get_args(typ)[0]
            origin = get_origin(typ)

        # Literal
        if origin is Literal:
            args = get_args(typ)
            literals = ", ".join(repr(a) for a in args)
            return f"Literal[{literals}]"

        # Union (Optional or other)
        if origin is Union:
            args = get_args(typ)
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                return f"Optional[{self._format_type(non_none[0])}]"
            else:
                inner = ", ".join(self._format_type(a) for a in args)
                return f"Union[{inner}]"

        # Generic containers
        if origin:
            args = get_args(typ)
            inner = ", ".join(self._format_type(a) for a in args)
            if inner:
                return f"{_get_type_name(origin)}[{inner}]"
            return _get_type_name(origin)

        #Simple type
        return _get_type_name(origin)

def _get_type_name(typ: type)->str:
    """Get a consistent name for a type object."""
    if hasattr(typ, '__name__'):
        return typ.__name__
    return str(typ)
    
def _get_type_bases(typ: type)->List[type]:
    if hasattr(typ, '__bases__'):
        return typ.__bases__ # type: ignore
    return []

def extract_class_interface_and_types(cls, output_dir="output"):
    """
    Main function to extract interface and types from a class.
    
    Args:
        cls: The class to analyze
        output_dir: Directory to save the generated files
    
    Returns:
        tuple: (interface_file_path, types_file_path)
    """
    extractor = TypeExtractor()
    return extractor.extract_from_class(cls, output_dir)

# Example class for testing
if __name__ == "__main__":
    from tau2.domains.airline.tools import AirlineTools
    # Extract interface and types
    interface_file, types_file = extract_class_interface_and_types(AirlineTools)
    print(f"Interface saved to: {interface_file}")
    print(f"Types saved to: {types_file}")
    print("Done")