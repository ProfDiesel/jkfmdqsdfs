from __future__ import annotations

from collections.abc import Mapping, Callable, Set, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from traceback import extract_stack, StackSummary
from typing import Any, TypeAlias, cast, Final, Generic, TypeVar, cast, override
from pydantic.dataclasses import dataclass as pdataclass


T = TypeVar('T')

@dataclass(frozen=True)
class BlackboardVar(Generic[T]):
    name: str
    default: T

    def __call__(self, value: T) -> BlackboardAssignment[T]:
        return BlackboardAssignment(key=self, value=value)

@dataclass(frozen=True)
class BlackboardAssignment(Generic[T]):
    key: BlackboardVar[T]
    value: T

Touched = Set[BlackboardVar[Any]] 
touched: Final[ContextVar[Touched]] = ContextVar('touched', default=set())

Callback: TypeAlias = Callable[['Blackboard'], Any]

@pdataclass(kw_only=True, frozen=True)
class CycleBreakerParams:
    max_recursive_calls: Final[int] = 25

class CycleBreaker:
    def __init__(self, *, max_recursive_calls: int):
        self.__max_recursive_calls: Final[int] = max_recursive_calls
        self.__recursive_calls: int = 0

    @contextmanager
    def __call__(self) -> Iterator:
        if self.__recursive_calls > self.__max_recursive_calls:
            stack: StackSummary = extract_stack()
            return
        try:
            self.__recursive_calls += 1
            yield
        finally:
            self.__recursive_calls -= 1

class Blackboard(Mapping[BlackboardVar[Any], Any]):
    def __init__(self, *, cycle_breaker: CycleBreaker) -> None:
        self.__dict: Final[dict[BlackboardVar[Any], Any]] = {} 
        self.__callbacks: Final[dict[Callback, Touched]] = {}
        self.__cyclebreaker: Final[CycleBreaker] = cycle_breaker

    @override
    def __len__(self) -> int:
        return len(self.__dict)

    @override
    def __iter__(self) -> Iterator[BlackboardVar[Any]]:
        return iter(self.__dict)

    @override
    def __getitem__(self, key: BlackboardVar[T]) -> T:
        touched.set(touched.get() | {key})
        return cast(T, self.__dict[key])

    def _call(self, callback: Callback) -> None:
        touched.set(set())
        callback(self)
        self.__callbacks[callback] = touched.get()

    def apply(self, *assignments: BlackboardAssignment[Any]) -> None:
        with self.__cyclebreaker():
            d = {assignment.key: assignment.value for assignment in assignments if assignment.value != self.__dict.get(assignment.key)}
            self.__dict.update(d)

            for callback, touched in self.__callbacks.items():
                if d.keys() & touched:
                    self._call(callback)        

    def register(self, callback: Callback) -> None:
        self._call(callback)        

    def unregister(self, callback: Callback) -> None:
        del self.__callbacks[callback]
