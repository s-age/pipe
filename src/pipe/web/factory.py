import inspect
from typing import Any, TypeVar, get_origin, get_type_hints

from pipe.core.container import DependencyContainer

T = TypeVar("T")


class GenericActionFactory:
    """Instantiates Actions by injecting dependencies based on type hints."""

    def __init__(self, container: DependencyContainer):
        self.container = container

    def create(self, action_class: type[T], runtime_context: dict[str, Any]) -> T:
        """
        Creates an instance of action_class, injecting dependencies.
        """
        # 0. Check for Singleton/Pre-registered Action instances
        if instance := self.container.get(action_class):
            return instance

        # If no __init__ or just object.__init__, use generic instantiation
        if action_class.__init__ is object.__init__:
            return action_class()

        signature = inspect.signature(action_class.__init__)
        try:
            type_hints = get_type_hints(action_class.__init__)
        except Exception:
            type_hints = {}

        inject_kwargs = {}

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            # Handle **kwargs (VAR_KEYWORD) and *args (VAR_POSITIONAL)
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                continue  # Ignore **kwargs, let it be empty
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                continue  # Ignore *args, let it be empty

            # 1. Check Runtime Context (Name match)
            if param_name in runtime_context:
                inject_kwargs[param_name] = runtime_context[param_name]
                continue

            param_type = type_hints.get(param_name)

            # 2. Check Runtime Context (Type match)
            if param_type:
                # Handle Generic Types
                check_type = param_type
                origin = get_origin(param_type)
                if origin is not None:
                    check_type = origin

                found_in_runtime = False
                for ctx_val in runtime_context.values():
                    try:
                        if isinstance(ctx_val, check_type):
                            inject_kwargs[param_name] = ctx_val
                            found_in_runtime = True
                            break
                    except TypeError:
                        continue
                if found_in_runtime:
                    continue

            # 3. Check DI Container
            if param_type:
                service = self.container.get(param_type)
                if service is not None:
                    inject_kwargs[param_name] = service
                    continue

            # 4. Check Default Value
            if param.default != inspect.Parameter.empty:
                continue

            # Optional: Allow None if type hint includes None (Optional[T])
            # This logic is a bit complex with get_origin/get_args,
            # for now we rely on explicit defaults.

            raise RuntimeError(
                f"Cannot resolve dependency '{param_name}: {param_type}' "
                f"for action '{action_class.__name__}'"
            )

        return action_class(**inject_kwargs)
