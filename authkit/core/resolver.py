import inspect
from typing import Type, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from authkit.core.adapters import AuthAdapters


class Resolver:
    """
    Dependency Resolver for AuthKit use cases.
    """
    
    @staticmethod
    def resolve(use_case_cls: Type, adapters: "AuthAdapters") -> Any:
        """
        Instantiates a use case class by injecting matching adapters.
        
        It inspects the `__init__` method of the use case and matches arguments
        by name or type against the properties in `AuthAdapters`.
        """
        sig = inspect.signature(use_case_cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # 1. Try to find by name in adapters
            if hasattr(adapters, param_name):
                val = getattr(adapters, param_name)
                
                # If dependency is explicitly missing (None) in the adapters (e.g. otp_store),
                # inject a Proxy that acts as a "poison pill". It will raise a clear error
                # only when the use case tries to ACCESS it.
                if val is None:
                    kwargs[param_name] = MissingDependencyProxy(param_name)
                else:
                    kwargs[param_name] = val
            
            # 2. (Optional) match by type...
            
        return use_case_cls(**kwargs)

class MissingDependencyProxy:
    """
    A placeholder for a missing dependency. 
    It raises a FeatureNotConfiguredError whenever any attribute is accessed or called.
    """
    def __init__(self, dependency_name: str):
        self._dependency_name = dependency_name

    def __getattr__(self, name):
        from authkit.exceptions.auth import FeatureNotConfiguredError
        raise FeatureNotConfiguredError(
            f"Cannot use feature because dependency '{self._dependency_name}' is not configured "
            f"in AuthAdapters."
        )
        
    def __call__(self, *args, **kwargs):
        from authkit.exceptions.auth import FeatureNotConfiguredError
        raise FeatureNotConfiguredError(
            f"Cannot use feature because dependency '{self._dependency_name}' is not configured "
            f"in AuthAdapters."
        )

