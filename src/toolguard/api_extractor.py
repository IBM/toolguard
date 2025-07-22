import ast
import inspect
from typing import Dict, List, Literal, Set, Tuple, get_type_hints, get_origin, get_args, Any
from typing import Annotated, Union
from pathlib import Path
import importlib
import sys
from collections import defaultdict, deque
import typing

class TypeExtractor:
    def __init__(self):
        self.module_roots = []
        self.collected_types = set()
        self.type_definitions = {}
        self.imports = set()
        self.processed_types = set()
        self.type_dependencies = defaultdict(set)  # type -> set of types it depends on
        self.literal_values = {}  # Store literal type values
        
    def extract_from_class(self, cls, output_dir="output"):
        """Extract interface and types from a class and save to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Get class name for file naming
        class_name = cls.__name__
        
        self.module_roots = [cls.__module__.split(".")[0]]

        # Extract interface
        interface_content = self._generate_interface(cls)
        
        # Extract all required types
        self._collect_all_types_from_class(cls)
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
    
    def _generate_interface(self, cls):
        """Generate the interface file content."""
        class_name = cls.__name__
        
        # Get type hints for the class
        try:
            type_hints = get_type_hints(cls)
        except:
            type_hints = {}
        
        # Start building the interface
        lines = []
        lines.append("# Auto-generated class interface")
        lines.append("from typing import *")
        lines.append("from abc import ABC, abstractmethod")
        lines.append(f"from {class_name.lower()}_types import *")
        lines.append("")
        
        # Get base classes (excluding BaseModel and object)
        bases = []
        for base in cls.__bases__:
            if base != object:
                bases.append(base.__name__)
        
            
        lines.append(f"class {class_name}(ABC):")
        
        # Add class docstring if available
        if cls.__doc__:
            docstring = cls.__doc__.strip()
            if docstring:
                lines.append(f'    """')
                # Handle multi-line docstrings
                for line in docstring.split('\n'):
                    lines.append(f'    {line.strip()}')
                lines.append(f'    """')
        
        # Get all methods
        methods = []
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not (name.startswith('_') or name in ['__init__', '__str__', '__repr__']):
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
    
    def _get_method_with_docstring(self, method, method_name):
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
    
    def _generate_class_definition(self, cls):
        """Generate a class definition with its fields."""
        lines = []
        class_name = cls.__name__
        
        # Skip BaseModel as it comes from Pydantic
        if class_name == 'BaseModel':
            return []
        
        # Determine base classes (excluding BaseModel and object)
        bases = []
        is_pydantic = False
        for base in cls.__bases__:
            if base != object and base.__name__ != 'BaseModel':
                bases.append(base.__name__)
            if hasattr(base, '__module__') and 'pydantic' in str(base.__module__):
                is_pydantic = True
        
        # Check if the class itself is pydantic
        if hasattr(cls, '__module__') and 'pydantic' in str(cls.__module__):
            is_pydantic = True
        
        inheritance = f"({', '.join(bases)})" if bases else ""
        lines.append(f"class {class_name}{inheritance}:")
        
        # Add class docstring if available
        if cls.__doc__:
            docstring = cls.__doc__.strip()
            if docstring:
                lines.append(f'    """')
                # Handle multi-line docstrings
                for line in docstring.split('\n'):
                    lines.append(f'    {line.strip()}')
                lines.append(f'    """')
        
        annotations = getattr(cls, '__annotations__', {})
        field_descriptions = self._extract_field_descriptions(cls)
        
        if annotations:
            for field_name, field_type in annotations.items():
                if not field_name.startswith('_'):
                    # Handle optional field detection by default=None
                    is_optional = False
                    default_val = getattr(cls, field_name, ...)
                    if default_val is None:
                        is_optional = True
                    elif hasattr(cls, '__fields__'):
                        # Pydantic field with default=None
                        field_info = cls.__fields__.get(field_name)
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
                    
                    if description and is_pydantic:
                        # Use Pydantic Field with description
                        lines.append(f'    {field_name}: {type_str} = Field(description="{description}")')
                    elif description:
                        # Add description as comment for non-Pydantic classes
                        lines.append(f'    {field_name}: {type_str}  # {description}')
                    else:
                        # No description available
                        lines.append(f'    {field_name}: {type_str}')
        else:
            lines.append("    pass")
        
        return lines
    
    def _extract_field_descriptions(self, cls):
        """Extract field descriptions from various sources."""
        descriptions = {}
        
        # Method 1: Check for Pydantic Field definitions
        if hasattr(cls, '__fields__'):  # Pydantic v1
            for field_name, field_info in cls.__fields__.items():
                if hasattr(field_info, 'field_info') and hasattr(field_info.field_info, 'description'):
                    descriptions[field_name] = field_info.field_info.description
                elif hasattr(field_info, 'description') and field_info.description:
                    descriptions[field_name] = field_info.description
        
        # Method 2: Check for Pydantic v2 model fields
        if hasattr(cls, 'model_fields'):  # Pydantic v2
            for field_name, field_info in cls.model_fields.items():
                if hasattr(field_info, 'description') and field_info.description:
                    descriptions[field_name] = field_info.description
        
        # Method 3: Check class attributes for Field() definitions
        for attr_name in dir(cls):
            if not attr_name.startswith('_'):
                try:
                    attr_value = getattr(cls, attr_name)
                    # Check if it's a Pydantic Field
                    if hasattr(attr_value, 'description') and attr_value.description:
                        descriptions[attr_name] = attr_value.description
                    elif hasattr(attr_value, 'field_info') and hasattr(attr_value.field_info, 'description'):
                        descriptions[attr_name] = attr_value.field_info.description
                except:
                    pass
        
        # Method 4: Parse class source for inline comments or docstrings
        try:
            source_lines = inspect.getsourcelines(cls)[0]
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
        if hasattr(cls, '__dataclass_fields__'):
            for field_name, field in cls.__dataclass_fields__.items():
                if hasattr(field, 'metadata') and 'description' in field.metadata:
                    descriptions[field_name] = field.metadata['description']
        
        return descriptions
    
    def _get_method_signature(self, method, method_name):
        """Extract method signature with type hints."""
        try:
            sig = inspect.signature(method)
            # Get type hints
            try:
                hints = get_type_hints(method)
            except:
                hints = {}
            
            params = []
            for param_name, param in sig.parameters.items():
                param_str = param_name
                
                # Add type annotation if available
                if param_name in hints:
                    type_str = self._format_type(hints[param_name])
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
            if 'return' in hints:
                return_type = self._format_type(hints['return'])
                return_annotation = f" -> {return_type}"
            elif sig.return_annotation != sig.empty:
                return_annotation = f" -> {sig.return_annotation}"
            
            params_str = ", ".join(params)
            return f"def {method_name}({params_str}){return_annotation}"
            
        except Exception as e:
            # Fallback for problematic signatures
            return f"def {method_name}(self, *args, **kwargs)"
    
    def _collect_all_types_from_class(self, cls):
        """Collect all types used in the class recursively."""
        # Get type hints from the class itself
        try:
            class_hints = get_type_hints(cls)
            for hint in class_hints.values():
                self._collect_types_recursive(hint)
        except:
            pass
        
        # Get type hints from all methods
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            try:
                method_hints = get_type_hints(method)
                for hint in method_hints.values():
                    self._collect_types_recursive(hint)
            except:
                pass
        
        # Also collect base class types
        for base in cls.__bases__:
            if base != object:
                self._collect_types_recursive(base)
    
    def _collect_types_recursive(self, type_hint):
        """Recursively collect all types from a type hint."""
        if type_hint in self.processed_types:
            return
            
        self.processed_types.add(type_hint)
        
        # Handle basic types
        if type_hint in (int, str, float, bool, bytes, None, type(None)):
            return

        if hasattr(type_hint, '__origin__') and hasattr(type_hint, '__args__'):
            self.collected_types.add(type_hint)
            for arg in type_hint.__args__:
                self._collect_types_recursive(arg)
                self._add_dependency(type_hint, arg)
            return
        
        # Handle typing constructs
        origin = get_origin(type_hint)
        args = get_args(type_hint)
        
        if origin is not None:
            # Handle Literal types specially
            if origin is typing.Literal or (hasattr(typing, '_LiteralGenericAlias') and 
                                         isinstance(type_hint, typing._LiteralGenericAlias)):
                self.collected_types.add(type_hint)
                # Store literal values
                self.literal_values[type_hint] = args
                return
            
            # Handle Union types (including Optional)
            if origin is typing.Union:
                self.collected_types.add(type_hint)
                for arg in args:
                    self._collect_types_recursive(arg)
                    self._add_dependency(type_hint, arg)
                return
            
            # Handle generic types like List[T], Dict[K, V], etc.
            self.collected_types.add(origin)
            for arg in args:
                self._collect_types_recursive(arg)
                # Add dependency relationship
                if hasattr(origin, '__name__'):
                    self._add_dependency(origin, arg)
        else:
            # Handle regular classes and custom types
            if hasattr(type_hint, '__module__') and hasattr(type_hint, '__name__'):
                self.collected_types.add(type_hint)
                
                # If it's a custom class, try to get its type hints
                if type_hint.__module__ not in ('builtins', 'typing'):
                    try:
                        nested_hints = type_hint.__annotations__
                        for field_name, nested_hint in nested_hints.items():
                            origin = get_origin(nested_hint)
                            if origin:
                                for arg in get_args(nested_hint):
                                    self._collect_types_recursive(arg)
                                    self._add_dependency(type_hint, arg)
                            else:
                                self._collect_types_recursive(nested_hint)
                                self._add_dependency(type_hint, nested_hint)

                        for base in reversed(type_hint.__mro__): #Base classes
                            self._collect_types_recursive(base)
                            self._add_dependency(type_hint, base)
                    except:
                        pass
    
    def _add_dependency(self, dependent_type, dependency_type):
        """Add a dependency relationship between types."""
        dep_name = self._get_type_name(dependent_type)
        dep_on_name = self._get_type_name(dependency_type)
        if dep_name != dep_on_name:
            self.type_dependencies[dependent_type].add(dependency_type)

    def _topological_sort_types(self, types):
        """Sort types by their dependencies using topological sort."""
        # Create a mapping of type names to types for easier lookup
        type_map = {self._get_type_name(t): t for t in types}
        
        # Build adjacency list and in-degree count
        adj_list = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize in-degree for all types
        for t in types:
            type_name = self._get_type_name(t)
            if type_name not in in_degree:
                in_degree[type_name] = 0
        
        # Build the dependency graph
        for dependent_type in types:
            dependent_name = self._get_type_name(dependent_type)
            for dependency_type in self.type_dependencies.get(dependent_type, set()):
                dependency_name = self._get_type_name(dependency_type)
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
        sorted_names = {self._get_type_name(t) for t in result}
        remaining = [t for t in types if self._get_type_name(t) not in sorted_names]
        result.extend(remaining)
        
        return result
    
    def _generate_types_file(self):
        """Generate the types file content."""
        lines = []
        lines.append("# Auto-generated type definitions")
        lines.append("from enum import Enum")
        lines.append("from abc import ABC")
        lines.append("from typing import *")
        lines.append("from datetime import datetime, date")
        lines.append("from decimal import Decimal")
        lines.append("from uuid import UUID")
        
        # Check if we need pydantic
        needs_pydantic = any(
            hasattr(t, '__module__') and 'pydantic' in str(t.__module__)
            for t in self.collected_types
            if hasattr(t, '__module__')
        )
        
        if needs_pydantic:
            lines.append("from pydantic import BaseModel, Field")
        
        lines.append("")
        
        # Group types by category
        custom_classes = []
        # type_aliases = []
        # literal_types = []
        # union_types = []
        
        for type_obj in self.collected_types:
            # Skip BaseModel as it comes from Pydantic
            if hasattr(type_obj, '__name__') and type_obj.__name__ == 'BaseModel':
                continue
                
            # Handle Literal types
            # if type_obj in self.literal_values:
            #     literal_types.append(type_obj)
            #     continue
            
            # # Handle Union types (including Optional)
            # origin = get_origin(type_obj)
            # if origin is typing.Union:
            #     union_types.append(type_obj)
            #     continue
            
            if not hasattr(type_obj, '__name__'):
                continue
            type_name = type_obj.__name__
            
            # Skip built-in and typing types
            if hasattr(type_obj, '__module__'):
                module_root = type_obj.__module__.split(".")[0]
                if module_root not in self.module_roots:
                    continue
            
            # Check if it's a class with attributes
            if (hasattr(type_obj, '__annotations__') or 
                (hasattr(type_obj, '__dict__') and 
                 any(not callable(getattr(type_obj, attr, None)) 
                     for attr in dir(type_obj) if not attr.startswith('_')))):
                custom_classes.append(type_obj)
            # else:
            #     # Treat as type alias
            #     type_aliases.append(type_obj)
        
        # Sort each category by dependencies
        # literal_types = self._topological_sort_types(literal_types)
        # union_types = self._topological_sort_types(union_types)
        # type_aliases = self._topological_sort_types(type_aliases)
        custom_classes = self._topological_sort_types(custom_classes)
        
        # # Generate Literal types first (they usually have no dependencies)
        # if literal_types:
        #     lines.append("# Literal types")
        #     for type_obj in literal_types:
        #         literal_def = self._generate_literal_definition(type_obj)
        #         lines.append(literal_def)
        #     lines.append("")
        
        # # Generate Union types (including Optional)
        # if union_types:
        #     lines.append("# Union types")
        #     for type_obj in union_types:
        #         union_def = self._generate_union_definition(type_obj)
        #         if union_def:
        #             lines.append(union_def)
        #     lines.append("")
        
        # # Generate type aliases
        # if type_aliases:
        #     lines.append("# Type aliases")
        #     for type_obj in type_aliases:
        #         lines.append(f"{type_obj.__name__} = {self._format_type(type_obj)}")
        #     lines.append("")
        
        # Generate custom classes (sorted by dependency)
        if custom_classes:
            lines.append("# Custom classes")
            for cls in custom_classes:
                class_def = self._generate_class_definition(cls)
                if class_def:  # Only add non-empty class definitions
                    lines.extend(class_def)
                    lines.append("")
        
        return "\n".join(lines)
    
    def _get_type_name(self, type_obj):
        """Get a consistent name for a type object."""
        if hasattr(type_obj, '__name__'):
            return type_obj.__name__
        else:
            return str(type_obj)
    
    def _generate_literal_definition(self, literal_type):
        """Generate definition for Literal types with their values."""
        values = self.literal_values.get(literal_type, [])
        
        # Format the values properly
        formatted_values = []
        for value in values:
            if isinstance(value, str):
                formatted_values.append(f'"{value}"')
            else:
                formatted_values.append(repr(value))
        
        values_str = ", ".join(formatted_values)
        
        # Try to create a meaningful name for the literal type
        if len(values) > 0:
            # # Use the first value or a combination to create a name
            # if isinstance(values[0], str):
            #     base_name = values[0].capitalize()
            # else:
            #     base_name = str(values[0]).capitalize()
            
            # Suggest meaningful name from context if possible
            type_name = self._get_type_name(literal_type)
            if type_name.startswith("Literal"):
                type_name = f"Literal_{abs(hash(str(literal_type))) % 10**6}"
        
        return f"{type_name} = Literal[{values_str}]"
    
    def _generate_union_definition(self, union_type):
        """Generate definition for Union types."""
        args = get_args(union_type)
        if not args:
            return None
        
        # Check if it's Optional (Union with None)
        if len(args) == 2 and type(None) in args:
            non_none_type = args[0] if args[1] is type(None) else args[1]
            type_name = f"Optional{self._get_type_name(non_none_type)}"
            formatted_type = self._format_type(non_none_type)
            return f"{type_name} = Optional[{formatted_type}]"
        else:
            # Regular Union type
            formatted_args = [self._format_type(arg) for arg in args]
            args_str = ", ".join(formatted_args)
            type_name = "Union" + "".join([
                self._get_type_name(arg) if hasattr(arg, '__name__') else str(arg)
                for arg in args
            ])
            return f"{type_name} = Union[{args_str}]"
    
    def _format_type(self, typ) -> str:
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
                return f"{origin.__name__}[{inner}]"
            return origin.__name__

        # Simple class
        if hasattr(typ, "__name__"):
            return typ.__name__

        return str(typ)



# Example usage
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