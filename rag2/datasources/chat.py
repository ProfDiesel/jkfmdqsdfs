from datetime import date, datetime
from pathlib import Path
from typing import Final, List, Literal, Tuple

from pydantic.dataclasses import dataclass
from pydantic import TypeAdapter
from jinja2 import Template

@dataclass(frozen=True, kw_only=True)
class Message:
    timestamp: datetime
    author: str
    message: str

@dataclass(frozen=True, kw_only=True)
class Chat:
    date: date
    messages: List[Message] 

CHAT_ADAPTER: Final[TypeAdapter] = TypeAdapter(Chat)

async def _search(store: VectorStore[Chat], query_vector: Vector, query: str, *, k: int = 4) -> list[tuple[Chat, Score]]:
    ...

DECAY_RATE = 0.9
DIVERSITY_FACTOR = 0.5


async def search(store: VectorStore[Chat], embedder: QueryEmbedder, query: str, *, k: int = 4, today: date | None = None) -> list[tuple[Chat, Score]]:
    if today is None:
        today = date.today()
    
    query_vector = await embedder(query)

    results = _search(store, query_vector, k = 100)
    results = maximal_marginal_relevance(query_vector, results, embedding_matrix, 1 - DIVERSITY_FACTOR)
    results = [(chat, score * (1.0 - DECAY_RATE) ^ (today - chat.date).days) for chat, score in results]
    return results


def maximal_marginal_relevance(sentence_vector, phrases, embedding_matrix, lambda_constant=0.5):
    """
    Return ranked phrases using MMR. Cosine similarity is used as similarity measure.
    :param sentence_vector: Query vector
    :param phrases: list of candidate phrases
    :param embedding_matrix: matrix having index as phrases and values as vector
    :param lambda_constant: 0.5 to balance diversity and accuracy. if lambda_constant is high, then higher accuracy. If lambda_constant is low then high diversity.
    :return: Ranked phrases with score
    """

    def cosine_similarity(a: Vector, b: Vector) -> float:
        from math import sqrt
        dot_product = sum(xa * xb for xa, xb in zip(a, b))
        magnitude_A = sqrt(sum(x * x for x in a))
        magnitude_B = sqrt(sum(x * x for x in b))
        return dot_product / (magnitude_A * magnitude_B)

    # todo: Use cosine similarity matrix for lookup among phrases instead of making call everytime.
    s = []
    r = sorted(phrases, key=lambda x: x[1], reverse=True)
    r = [i[0] for i in r]
    while len(r) > 0:
        score = 0
        phrase_to_add = ''
        for i in r:
            # accuracy
            first_part = cosine_similarity([sentence_vector], [embedding_matrix.loc[i]])[0][0]
            # diversity
            second_part = 0
            for j in s:
                cos_sim = cosine_similarity([embedding_matrix.loc[i]], [embedding_matrix.loc[j[0]]])[0][0]
                if cos_sim > second_part:
                    second_part = cos_sim
            equation_score = lambda_constant*(first_part)-(1-lambda_constant) * second_part
            if equation_score > score:
                score = equation_score
                phrase_to_add = i
        if phrase_to_add == '':
            phrase_to_add = i
        r.remove(phrase_to_add)
        s.append((phrase_to_add, score))
    return s