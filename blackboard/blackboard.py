from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, Any, TYPE_CHECKING, Unpack, TypeAlias, cast, Final, Generic, TypeVar, cast, override, Literal, Self
from collections.abc import Mapping, Callable, Set, Iterator
from enum import Enum, auto
from inspect import signature, Signature, Parameter
import asyncio
#import aiorwlock

from contextvars import ContextVar

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

class Blackboard(Mapping[BlackboardVar[Any], Any]):
    def __init__(self) -> None:
        self.__dict: dict[BlackboardVar[Any], Any] = {} 
        self.__callbacks: dict[Callback, Touched] = {}

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
        d = {assignment.key: assignment.value for assignment in assignments if assignment.value != self.__dict.get(assignment.key)}
        self.__dict |= d

        for callback, touched in self.__callbacks.items():
            if d.keys() & touched:
                self._call(callback)        

    def register(self, callback: Callback) -> None:
        self._call(callback)        

    def unregister(self, callback: Callback) -> None:
        del self.__callbacks[callback]

CONFIG: BlackboardVar[str | None] = BlackboardVar('config', None)
VERSION: BlackboardVar[str | None] = BlackboardVar('version', None)

bb = Blackboard()

def f(blackboard: Blackboard):
    bb.apply(VERSION('1.0'))

def g(blackboard: Blackboard):
    print('youhou')

bb.register(f)
bb.register(g)

bb.apply(CONFIG('ipo'))
