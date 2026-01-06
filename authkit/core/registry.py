from typing import Type, TypeVar, Dict

T = TypeVar("T")

class Registry:
    """
    A simple registry to hold use case classes.
    """
    _use_cases: Dict[str, Type] = {}

    @classmethod
    def register(cls, name: str):
        """
        Decorator to register a use case class.
        
        Args:
            name: Custom name for the use case property. Must be a non-empty string.
        """
        if not name:
             raise ValueError("Registry.register() require a non-empty name string.")

        def decorator(use_case_cls: Type):
            # No auto-naming anymore
            cls._use_cases[name] = use_case_cls
            return use_case_cls
        return decorator

    @classmethod
    def items(cls):
        return cls._use_cases.items()
