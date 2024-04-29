from datetime import date, datetime
from pathlib import Path
from typing import Final, cast, TypeVar
from collections.abc import Sequence

import orjson
from jinja2 import Template
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

from .vectorstore import Score, Vector, VectorStore
from ..endpoint import QueryEmbedder

T = TypeVar('T')


@dataclass(frozen=True, kw_only=True)
class Message:
    timestamp: datetime
    author: str
    message: str

@dataclass(frozen=True, kw_only=True)
class Chat:
    date: date
    messages: list[Message] 

CHAT_ADAPTER: Final[TypeAdapter] = TypeAdapter(Chat)

FIRST_PASS_K = 25
DECAY_RATE = 0.9
DIVERSITY_FACTOR = 0.5

# https://medium.com/tech-that-works/maximal-marginal-relevance-to-rerank-results-in-unsupervised-keyphrase-extraction-22d95015c7c5
def maximal_marginal_relevance(sentence_vector: Vector, phrases: Sequence[tuple[float, T]], embedding_matrix: Sequence[Vector], lambda_constant=0.5) -> list[tuple[int, float]]:
    def cosine_similarity(a: Vector, b: Vector) -> float:
        from math import sqrt
        dot_product = sum(xa * xb for xa, xb in zip(a, b))
        magnitude_A = sqrt(sum(x * x for x in a))
        magnitude_B = sqrt(sum(x * x for x in b))
        return dot_product / (magnitude_A * magnitude_B)

    s: list[tuple[int, float]] = []
    r: list[int] = [i[0] for i in sorted(enumerate(phrases), key=lambda x: x[1], reverse=True)]
    while len(r) > 0:
        def compute_score(i: int) -> float:
            accuracy = cosine_similarity(sentence_vector, embedding_matrix[i])
            diversity = max(cosine_similarity(embedding_matrix[i], embedding_matrix[j]) for j,_ in s)
            return lambda_constant*(accuracy)-(1-lambda_constant) * diversity 
        score, to_add = max((compute_score(i), i) for i in r)
        r.remove(to_add)
        s.append((to_add, score))
    return s


async def search(store: VectorStore[Chat], embedder: QueryEmbedder, query: str, *, today: date | None = None, k: int = 4) -> list[tuple[Chat, Score]]:
    if today is None:
        today = date.today()
    
    query_vector = await embedder(query)

    results: list[tuple[Chat, Vector, Score]] = [(CHAT_ADAPTER.validate_json(payload), orjson.loads(embedding), cast(Score, distance)) for payload, embedding, distance in store.connection.execute( f"""
        SELECT payload, embedding, distance
        FROM {store.table} e
        INNER JOIN vss_{store.table} v on v.rowid = e.rowid  
        WHERE vss_search(v.embedding, vss_search_params('{orjson.dumps(query_vector).decode()}', {FIRST_PASS_K}))
    """)]
    results = maximal_marginal_relevance(query_vector, results, embedding_matrix, 1 - DIVERSITY_FACTOR)
    results = [(chat, score * (1.0 - DECAY_RATE) ^ (today - chat.date).days) for chat, score in results]
    return results


