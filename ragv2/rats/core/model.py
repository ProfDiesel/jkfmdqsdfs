from __future__ import annotations
from dataclasses import dataclass
from typing import NewType
from pandas import DataFrame
from numpy import ndarray, dtype, float64
from typing import Literal, Any, Protocol, Final, TypeAlias, Tuple
from collections.abc import Mapping, Collection, Sequence
from functools import reduce
from operator import or_

Embedding = NewType('Embedding', ndarray[Literal[768], dtype[float64]])

DocumentId = NewType('DocumentId', str)
Location = NewType('Location', int) # location of the chunk in the document
ChunkId: TypeAlias = Tuple[DocumentId, Location]

Metadata = NewType('Metadata', Mapping[str, Any])


class Database:
    def __init__(self, sqlite_connection, es_client):
        pass

    def get_hollow_docs(self, ids: Collection[DocumentId]) -> list[Document]:
        ''' without chunks '''
        pass

    def get_docs(self, ids: Collection[DocumentId]) -> list[Document]:
        pass

    def inplace_fill_documents(self, docs: Collection[Document]) -> None:
        pass

class NotResolved:
    pass
NOT_RESOLVED: Final[NotResolved] = NotResolved()


class Document(Protocol):
    @property
    def id(self) -> DocumentId: ...

    @property
    def chunks(self) -> Sequence[Chunk] | NotResolved: ...

    # sorted by location
    async def get_chunks(self) -> Sequence[Chunk]: ...

    @property
    def embedding(self) -> Embedding | NotResolved: ...

    def get_text(self, *, separator: str = '\n') -> str | NotResolved: ...
    
    @property
    def text(self) -> str | NotResolved: ...

    @property
    def metadata(self) -> Metadata | NotResolved: ...

    @property
    def kpis(self) -> DocumentKpis: ...

    
class DocumentMixin:
    def __init__(self) -> None:
        self.__chunks: Sequence[Chunk] | NotResolved = NOT_RESOLVED

    @property
    def chunks(self) -> Sequence[Chunk] | NotResolved:
        return self.__chunks

    @property
    def embedding(self) -> Embedding | NotResolved:
        if self.chunks is NOT_RESOLVED:
            return NOT_RESOLVED 
        return normalized(sum(chunk.embedding for chunk in self.chunks))

    def get_text(self, *, separator: str = '\n') -> str | NotResolved:
        if self.chunks is NOT_RESOLVED:
            return NOT_RESOLVED 
        return separator.join(chunk.text for chunk in self.chunks)
    text = property(get_text)

    @property
    def metadata(self) -> Metadata | NotResolved: 
        if self.chunks is NOT_RESOLVED:
            return NOT_RESOLVED 
        return reduce(or_, (chunk.metadata for chunk in self.chunks))
    

class Chunk(Protocol):
    @property
    def id(self) -> ChunkId: ...

    @property
    def embedding(self) -> Embedding: ...

    @property
    def document(self) -> Document | NotResolved: ...

    async def get_document(self) -> Document: ... 

    @property
    def location(self) -> Location: ...

    @property
    def text(self) -> str: ...

    @property
    def metadata(self) -> Metadata: ...

    @property
    def kpis(self) -> ChunkKpis: ...


class OrmModel:
    def __init__(self):
        self.__orm_manager = ...

    async def flush(self) -> None:
        self.__orm_manager.flush(self)


@dataclass(kw_only=True)
class DocumentKpis(OrmModel):
    nb_attributions: int
    total_utilization: float

    @property
    def utilization(self) -> float:
        return self.total_utilization / self.nb_attributions

    def update(self, *, utilization: float) -> None:
        self.nb_attributions += 1
        self.total_utilization += utilization


@dataclass(kw_only=True)
class ChunkKpis(OrmModel):
    id: ChunkId
    nb_attributions: int


@dataclass(frozen=True, kw_only=True)
class RagResponseMetrics:
    completeness: float
    context_adherence: float

