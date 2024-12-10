from typing import Protocol
from dataclasses import dataclass
from .blackboard import Callback, Blackboard, BlackboardVar
from collections.abc import Sequence, Collection
from usearch.index import Index, Match

@dataclass
class Message:
    pass

MESSAGES: BlackboardVar[Sequence[Message]] = BlackboardVar('messages', [])

@dataclass
class Embeddings:
    pass

@dataclass
class Strategy:
    embeddings: Embeddings
    agents: list[Callback]
    chain_of_thought: str


class Controller:
    def get_strategy(self) -> Strategy:
        raise NotImplementedError()

    def __init__(self, strategies: Sequence[Strategy]):
        index = Index(
            ndim=3, # Define the number of dimensions in input vectors
            metric='cos', # Choose 'l2sq', 'haversine' or other metric, default = 'ip'
            dtype='f32', # Quantize to 'f16' or 'i8' if needed, default = 'f32'
            connectivity=16, # How frequent should the connections in the graph be, optional
            expansion_add=128, # Control the recall of indexing, optional
            expansion_search=64, # Control the quality of search, optional
        )
        index.add(range(len(strategies)), (strategy.embeddings for strategy in strategies))

    def chose(blackboard: Blackboard):
        chat_embedding = embed(blackboard[MESSAGES])
        self.__index.search()
"""
Le système a émis les suggestions suivantes:
{% for agent in agents %}
- {{ agent.suggestion }}
{% endfor %}
"""