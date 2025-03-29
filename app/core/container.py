import inspect
from typing import Any, Callable, Dict, Generator, Optional, Tuple, get_type_hints

import typing_inspect


def _unwrap_type_hint(t: Any) -> Any:
    if typing_inspect.is_optional_type(t):
        return next(
            (_unwrap_type_hint(th) for th in typing_inspect.get_args(t) if th), Any
        )
    return t


def _get_type_hints(handler: Callable) -> Dict[str, Any]:
    func: Callable = handler

    if isinstance(handler, type):
        for bt in handler.__mro__:
            if "__init__" in bt.__dict__:
                func = handler.__init__
                break
            elif "__new__" in bt.__dict__:
                func = handler.__new__
                break

    type_hints = get_type_hints(func)

    sig = inspect.signature(func)
    for p_name in sig.parameters:
        if p_name not in type_hints and p_name not in ("self", "cls", "args", "kwargs"):
            type_hints[p_name] = Any

    type_hints.pop("return", None)
    return type_hints


def _get_spec(
    dependency: Callable,
) -> Generator[Tuple[str, Any, bool, Any, bool], None, None]:
    for name, type_hint in _get_type_hints(dependency).items():
        unwrapped_type_hint = _unwrap_type_hint(type_hint)
        yield (
            name,
            type_hint,
            typing_inspect.is_optional_type(type_hint),
            unwrapped_type_hint,
            unwrapped_type_hint is Any,
        )


class Provider:
    @classmethod
    def of(cls, dependency: Any, provider: Any):
        if isinstance(provider, Provider):
            assert provider.dependency == dependency
            return provider
        return cls(dependency=dependency, provider=provider)

    def __init__(self, dependency: Any, provider: Any):
        self.dependency = dependency
        self.provider = provider

    def resolve(self, di: "Container") -> Any:
        if isinstance(self.provider, Resolved):
            return self.provider.res
        elif not callable(self.provider):
            return self.provider
        params = di.collect_params(self.provider)
        return self.provider(**params)


class Resolved:
    def __init__(self, resolution: Any) -> None:
        self.res = resolution


class DepRegistry:
    def __init__(self) -> None:
        self._providers: Dict[Any, Provider] = {}

    def _store(self, provider: Provider) -> None:
        self._providers[provider.dependency] = provider

    def register(
        self, dependency: Any, provider: Any = None, value: Any = None
    ) -> None:
        if value is not None:
            provider = Resolved(resolution=value)
        self._store(provider=Provider.of(dependency, provider))

    def is_registered(self, dependency: Any) -> bool:
        return dependency in self._providers

    def __getitem__(self, dependency: Any) -> Provider:
        if not self.is_registered(dependency):
            raise KeyError(f"No registered dependency {dependency}")
        return self._providers[dependency]

    @staticmethod
    def _copy_of_providers(
        providers: Dict[Any, Provider], deep: bool = False
    ) -> Dict[Any, Provider]:
        if deep:
            return {
                p.dependency: Provider.of(p.dependency, p.provider)
                for p in providers.values()
            }
        else:
            return providers

    def clone(self, *others: "DepRegistry", deep: bool = False) -> "DepRegistry":
        deps = DepRegistry()
        deps._providers.update(self._copy_of_providers(self._providers, deep=deep))
        for other in others:
            deps._providers.update(self._copy_of_providers(other._providers, deep=deep))
        return deps


class DepRegistryProxy:
    def __init__(self) -> None:
        self._dependencies = DepRegistry()

    def register(
        self, dependency: Any, provider: Any = None, value: Any = None
    ) -> None:
        self._dependencies.register(dependency, provider=provider, value=value)

    @property
    def dependencies(self) -> DepRegistry:
        return self._dependencies


class Container(DepRegistryProxy):
    def __init__(self, *, dependencies: DepRegistry = None, name: str = None) -> None:
        super().__init__()
        if dependencies:
            self._dependencies = dependencies
        self._name = name
        self.resolution_cache: Dict[Any, Any] = {}

    def clone(self, *others: "Container", deep: bool = False, **kwargs) -> "Container":
        dep_others = []
        if others:
            dep_others = [c.dependencies for c in others]
        dep_clone = self.dependencies.clone(*dep_others, deep=deep)
        return Container(dependencies=dep_clone, **kwargs)

    def provides(self, dependency: Any) -> bool:
        return self._dependencies.is_registered(dependency)

    def register_and_resolve(self, dependency: Any, provider: Any, **kwargs) -> Any:
        self.register(dependency, provider=provider, **kwargs)
        return self.resolve(dependency)

    def collect_params(self, resolution: Callable) -> Dict[str, Any]:
        params = {}

        for name, type_hint, is_optional, unwrapped_type_hint, is_any in _get_spec(
            resolution
        ):
            try:
                params[name] = self.resolve(name)
                continue
            except Exception as e:
                if is_any:
                    print(
                        f"Error resolving dependency {name} for type {type_hint}, {e}"
                    )
                    continue

            try:
                params[name] = self.resolve(unwrapped_type_hint)
            except Exception as e:
                if not is_optional:
                    print(
                        f"Error resolving dependency {name} for type {unwrapped_type_hint}, {e}"
                    )

        return params

    def clear_cache(self, dependency: Optional[Any]):
        if dependency is None:
            self.resolution_cache = {}
        if dependency in self.resolution_cache:
            del self.resolution_cache[dependency]

    def register(
        self, dependency: Any, provider: Any = None, value: Any = None
    ) -> None:
        self.clear_cache(dependency)
        super().register(dependency, provider=provider, value=value)

    def resolve(self, dependency: Any) -> Any:
        if dependency is Container:
            return self

        if self.provides(dependency):
            if dependency not in self.resolution_cache:
                provider = self.dependencies[dependency]
                resolution = provider.resolve(self)

                self.resolution_cache[dependency] = resolution
            return self.resolution_cache[dependency]

        params = self.collect_params(dependency)
        res = dependency(**params)
        provider = Provider.of(dependency, Resolved(res) if callable(res) else res)
        return self.register_and_resolve(dependency, provider=provider)
