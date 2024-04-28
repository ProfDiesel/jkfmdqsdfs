from __future__ import annotations
from dataclasses import dataclass
import asyncio
from .prompt import prompts 
from .compose import sync, Pipe, parallel 
from .endpoint import Endpoint, LLM, QueryEmbedder
from typing import Callable, Iterable, TypedDict, Any
from functools import partial
from .issue import IssueFeatures

class IssueDetectorInput(TypedDict):
    chat_history: str

class IssueFeatureExtractionInput(TypedDict):
    chat_history: str

    
def issue_detection_chain(llm: LLM) -> Pipe[[str], bool]:
    s: Callable[[str], IssueDetectorInput] = lambda s: {'chat_history': s} 
    return (Pipe(sync(s))
          | prompts[('detect_errors', IssueDetectorInput)]
          | llm
          | sync(lambda x: x == 'YES')
          )

def issue_feature_extraction_chain(llm: LLM) -> Pipe[[str], IssueFeatures]:
    s: Callable[[str], IssueFeatureExtractionInput] = lambda s: {'chat_history': s} 
    return (Pipe(sync(s))
          | partial(prompts[('extract', IssueFeatureExtractionInput)], output_type=IssueFeatures)
          | llm
          | sync(IssueFeatures.model_validate_json)
          )

def doc_retrieval_chain(embedder: QueryEmbedder) -> Pipe[[str], list[tuple[Document, Score]]]:
    def consolidate():
        pass

    def litm_reorder(documents: list[T]) -> list[T]:
        """https://arxiv.org/abs//2307.03172"""

        documents.reverse()
        reordered_result: list[T] = []
        for i, value in enumerate(documents):
            if i % 2 == 1:
                reordered_result.append(value)
            else:
                reordered_result.insert(0, value)
        return reordered_result

    return (Pipe()
        | parallel(
            jiras_source = jira_retriever,
            chat_source = chat_retriever | process_chat_results,
            userguide_source = userguide_retriever,
            confluence_source = confluence_retriever,
            origin = sync(lambda x: x)
        )
        | consolidate
        | litm_reorder
    )


