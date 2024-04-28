from dataclasses import dataclass
from collections.abc import Iterable
from requests import post
from asyncio import to_thread
from pydantic import HttpUrl
from typing import Final, Protocol, TypeAlias, Sequence, Annotated, Generic, TypeVar

class LLM(Protocol):
    async def __call__(self, query: str, *, model_name: str = '', max_token: int = 1024) -> str: ...

N = TypeVar('N', covariant=True)

Vector: TypeAlias = Annotated[Sequence[float], N]

class Embedder(Protocol, Generic[N]):
    async def __call__(self, texts: Iterable[str]) -> Iterable[Vector[N]]: ...

class QueryEmbedder(Protocol):
    async def __call__(self, text: str) -> Vector[N]: ...


class Endpoint:
    def __init__(self) -> None:
        self.__url: Final[HttpUrl] = 'http://'

    async def llm(self, query: str, *, model_name: str = '', max_token: int = 1024) -> str:
        return await to_thread(post(self.__url, json={}))

    @property
    def dimensionality(self) -> int:
        return 10

    async def embed(self, texts: Iterable[str]) -> Iterable[Vector]:
        return []

    async def query(self, text: str) -> Vector:
        return []

