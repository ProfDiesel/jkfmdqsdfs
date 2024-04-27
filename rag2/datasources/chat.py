from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Final, List, Literal, Tuple

from jinja2 import Template
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain_community.vectorstores.sqlitevss import SQLiteVSS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain.retrievers import EnsembleRetriever

@dataclass(frozen=True, kw_only=True)
class Message:
    timestamp: datetime
    author: str
    message: str

@dataclass(frozen=True, kw_only=True)
class Chat:
    date: date
    messages: List[Message] 

    def as_document(self, template: Template) -> Document:
        return Document(page_content=template.render(chat=self), metadata={'date': self.date})


class ChatEmbedder:
    def __init__(self, db_file: Path, table: str, embeddings: Embeddings):
        self.__vectorstore: Final[SQLiteVSS] = SQLiteVSS(table=table, connection=None, embedding=embeddings)
        self.__template: Final[Template]

    def add_jira(self, chats: List[Chat]) -> List[str]:
        return [self.__vectorstore.add_documents([chat.as_document(self.__template)], current_time=chat.date)[0] for chat in chats]


def get_retriever(db_file: Path, table: str, embeddings: Embeddings) -> BaseRetriever:
    vectorstore = SQLiteVSS(table=table, connection=None, embedding=embeddings)
    # semantic_similarity + (1.0 - decay_rate) ^ hours_passed
    time_weighted_retriever = TimeWeightedVectorStoreRetriever(vectorstore=vectorstore, decay_rate=0.01, search_kwargs={'include_metadata': True})
    # days tend to be similar
    mmr_retriever = vectorstore.as_retriever(search_type='mmr', search_kwargs={'k': 5, 'include_metadata': True})
    ensemble_retriever = EnsembleRetriever(retrievers=[time_weighted_retriever, mmr_retriever], weights=[0.5, 0.5])
    return ensemble_retriever 