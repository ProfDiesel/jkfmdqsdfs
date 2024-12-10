from __future__ import annotations

from asyncio import iscoroutinefunction, gather
from functools import partial, wraps
from typing import (Awaitable, Callable, Final, Generic, ParamSpec, Protocol, TypeVar,
                    overload, Any, cast)

P = ParamSpec('P')
T = TypeVar('T', covariant=True)
P0 = ParamSpec('P0')
P1 = ParamSpec('P1')
T0 = TypeVar('T0')
T1 = TypeVar('T1')

@overload
def sync(function: Callable[P, Awaitable[T]], /) -> Callable[P, Awaitable[T]]: ...


@overload
def sync(function: Callable[P, T], /) -> Callable[P, Awaitable[T]]: ...


def sync(function: Callable[P, T | Awaitable[T]], /) -> Callable[P, Awaitable[T]]:
    if iscoroutinefunction(function):
        return function

    @wraps(function)
    async def async_wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        result = function(*args, **kwargs)
        if isinstance(result, Awaitable):
            return await result
        return result

    return async_wrapped


async def parallel(**functions: Callable[P, Awaitable[Any]]) -> Callable[P, Awaitable[dict[str, Any]]]:
    async def apply_and_gather(*args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
        return dict(zip(functions.keys(), await gather(*(function(*args, **kwargs) for function in functions.values()))))
    return apply_and_gather


class Pipe(Protocol, Generic[P, T]):
    @overload
    def __init__(self, lhs: Callable[P, Awaitable[T0]], rhs: Callable[[T0], Awaitable[T]]): ...

    @overload
    def __init__(self, lhs: Callable[P, Awaitable[T]]): ...

    def __init__(self, lhs: Callable[P, Awaitable[T0]], rhs: Callable[[T0], Awaitable[T]] | None = None) -> None: ...

    def __or__(self, rhs: Callable[[T], Awaitable[T1]]) -> Pipe[P, T1]: ...

    def __ror__(self: Pipe[[T0], T], lhs: Callable[P0, Awaitable[T0]]) -> Pipe[P0, T]: ...

    async def __lt__(self: Pipe[[T0], T], args: T0) -> T: ...

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T: ...

    def __get__(self, instance, owner): ...

PipeT = TypeVar('PipeT', covariant=True)

class DefaultPipe(Generic[P, T]):
    @staticmethod
    def compose(lhs: Callable[P, Awaitable[T0]], rhs: Callable[[T0], Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        async def composite(*args, **kwargs):
            return await rhs(await lhs(*args, **kwargs))
        return composite

    @overload
    def __init__(self, lhs: Callable[P, Awaitable[T0]], rhs: Callable[[T0], Awaitable[T]]): ...

    @overload
    def __init__(self, lhs: Callable[P, Awaitable[T]]): ...

    def __init__(self, lhs: Callable[P, Awaitable[T0]], rhs: Callable[[T0], Awaitable[T]] | None = None) -> None:
        self.__f: Final[Callable[P, Awaitable[T]]] = self.compose(lhs, rhs) if rhs is not None else cast(Callable[P, Awaitable[T]], lhs)

    def __or__(self: Pipe[P, T], rhs: Callable[[T], Awaitable[T1]]) -> Pipe[P, T1]:
        return type(self)(self.__f, rhs)

    def __ror__(self: Pipe[[T0], T], lhs: Callable[P0, Awaitable[T0]]) -> Pipe[P0, T]:
        return type(self)(lhs, self.__f)

    async def __lt__(self: Pipe[[T0], T], args: T0) -> T:
        return await self(args)

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return await self.__f(*args, **kwargs)

    def __get__(self, instance, owner):
        return partial(self, instance) if instance else self

class Maybe(DefaultPipe):

    @staticmethod
    def compose(first, second):
        def composite(*args, **kwargs):
            result = first(*args, **kwargs)
            return second(result) if is_valid(result) else result
        return composite

    def __call__(self, *args, **kwargs):
        match args, kwargs:
            case [(x,), {}] if not is_valid(x):
                return x
            case _:
                return super()(*args, **kwargs)    
            