from __future__ import annotations

from datetime import datetime, timedelta
from dataclasses import dataclass
from ..core.model import Embedding
from typing import NewType, TypeVar, Any
from collections.abc import Mapping 
from math import log2
from functools import reduce
from typing import Final

import numpy as np

from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import paired_cosine_distances

T = TypeVar('T')

Token = NewType('Token', str)

@dataclass
class Message:
    timestamp: datetime
    author: str
    # other referenced users
    ats: list[str]
    text: str

# square matrix of proximity between members
authors_social_proximity: Any

# TODO: neighbourhood in users, like every APS member are close, give more weight to 'ats'
def social_vector(author: str, ats: list[str]) -> Mapping[str, float]: ...

def embed(texts: list[str]) -> list[Embedding]: ...


# weight important tokens with TF-IDF with a stopword list ?
# ELSER ?
def tokenize(text: str) -> Mapping[Token, float]: ...


def log2_inverse_distance(x0: T, x1: T, unit: T):
    return log2(1 + 1 / (1 + abs((x0 - x1) / unit)))

def to_item_matrix(bags: list[Mapping[T, float]]):
    all_keys = list(reduce(set.union, (bag.keys() for bag in bags), set()))
    return np.fromfunction(lambda tokens, index: tokens.get(all_keys[index], 0), shape=(len(bags), len(all_keys)))

def detect_threads(messages: list[Message]) -> tuple[list[Message], list[Message]]:
    TIME_DISTANCE_UNIT: Final[timedelta] = timedelta(seconds=10)

    embeddings = embed([message.text for message in messages])
    embeddings_distances = paired_cosine_distances(embeddings, embeddings)

    tokens = to_item_matrix([tokenize(message.text) for message in messages])
    token_distances = paired_cosine_distances(tokens, tokens)

    social_footprint = to_item_matrix([social_vector(message.author, message.ats) * authors_social_proximity for message in messages])
    social_distances = paired_cosine_distances(social_footprint, social_footprint)

    time_distances = np.fromfunction(lambda index0, index1: log2_inverse_distance(messages[index0].timestamp, messages[index1].timestamp, TIME_DISTANCE_UNIT), shape=(len(messages), len(messages)))

    distances = embeddings_distances * token_distances * social_distances * time_distances

    clustering = AgglomerativeClustering(n_clusters=2, metric='precomputed', linkage='average')
    result = clustering.fit(distances)
    c0 = [message for message, label in zip(messages, result.labels_) if label == 0]
    c1 = [message for message, label in zip(messages, result.labels_) if label == 1]
    return (c0, c1)