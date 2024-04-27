from requests import post
from asyncio import to_thread
from pydantic import HttpUrl
from typing import Final, Protocol, TypeAlias, Sequence

class LLM(Protocol):
    async def __call__(self, query: str, *, model_name: str = '', max_token: int = 1024) -> str: ...

Vector: TypeAlias = Sequence[float]

class Embedder(Protocol):
    async def __call__(self, texts: Sequence[str]) -> Sequence[Vector]: ...

class QueryEmbedder(Protocol):
    async def __call__(self, text: str) -> Vector: ...


class Endpoint:
    def __init__(self) -> None:
        self.__url: Final[HttpUrl] = 'http://'

    async def llm(self, query: str, *, model_name: str = '', max_token: int = 1024) -> str:
        return await to_thread(post(self.__url, json={}))

    async def embed(self, texts: Sequence[str]) -> Sequence[Vector]:
        return []

    async def query(self, text: str) -> Vector:
        return []

