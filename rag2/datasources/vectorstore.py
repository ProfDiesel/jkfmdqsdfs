from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import (Final, Generic, Literal, NewType, Protocol, TypeVar,
                    cast)

import apsw
import apsw.bestpractice
import orjson
import sqlite_semver
import sqlite_vss
from apsw import Connection
from jinja2 import Template

from ..endpoint import Embedder, Vector

T = TypeVar('T')

SQLiteURL = Path | Literal['']

DocumentId = NewType('DocumentId', int)
Score = NewType('Score', float)

apsw.bestpractice.apply(apsw.bestpractice.recommended)

class Retriever(Protocol, Generic[T]):
    async def __call__(self, query: str, *, k: int = 4) -> list[tuple[T, Score]]: ...


class VectorStore(Generic[T]):
    def __init__(self, url: SQLiteURL, table: str, *, write = False):
        self.__connection: Final[Connection] = Connection(str(url), flags=(apsw.SQLITE_OPEN_CREATE | apsw.SQLITE_OPEN_READWRITE) if write else apsw.SQLITE_OPEN_READONLY)
        self.__connection.enable_load_extension(True)
        sqlite_vss.load(self.__connection)
        sqlite_semver.load(self.__connection)
        self.__table: Final[str] = table

    @property
    def connection(self) -> Connection:
        return self.__connection

    @property
    def table(self) -> str:
        return self.__table

    async def insert(self, template: Template, embedder: Embedder, items: Sequence[T]) -> Iterable[DocumentId]:
        embeddings: Sequence[Vector] = list(await embedder(template.render(items) for item in items))
        return (cast(DocumentId, rowid) for (rowid,) in self.__connection.executemany(
            f"INSERT INTO {self.__table}(payload, embedding) VALUES (?, ?) RETURNING rowid",
            [(orjson.dumps(item), orjson.dumps(embedding)) for item, embedding in zip(items, embeddings)]))




