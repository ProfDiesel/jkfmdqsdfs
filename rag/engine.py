from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING, Sequence, Optional, List, cast

from langchain.output_parsers import BooleanOutputParser

if TYPE_CHECKING:
    from langchain_core.callbacks import Callbacks
    from langchain_core.documents import Document
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.chains.history_aware_retriever import \
        create_history_aware_retriever
    from langchain.globals import set_debug, set_verbose
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import (Runnable, RunnablePassthrough,
                                        RunnableSerializable)

    from langchain_core.documents.compressor import BaseDocumentCompressor
    from langchain_core.retrievers import RetrieverLike 

    from langchain_community.document_transformers import (
        LongContextReorder,
    )

from .irc import IRCClient
from .prompts import load_prompt
from .datasources.jira import JiraTool
from .datasources.chat import get_retriever
from .issue import Issue, create_issue_extractor

set_verbose(True)

class IssueDetectorInput(TypedDict):
    chat_history: str

class ContextualizeInput(TypedDict):
    chat_history: str


class DocumentCompressor(BaseDocumentCompressor):
    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        return documents

class Engine:
    def __init__(self, client: IRCClient, llm: BaseLanguageModel):
        self.__client = client
        
        self.__issue_detector_chain = cast(Runnable[IssueDetectorInput, bool], (
            load_prompt('detect_errors', input_type=IssueDetectorInput)
            | llm
            | BooleanOutputParser()
        ).with_config(run_name='issue_detector_chain'))

        issue_extractor_chain = create_issue_extractor(load_prompt('extract_issue_features', input_type=IssueDetectorInput), llm)

        self.__retriever_gatherer: RetrieverLike = (
            RunnablePassthrough()
            | { 'jiras_source': jira_retriever,
                'chat_source': chat_retriever | process_chat_results,
                'userguide_source': userguide_retriever,
                'confluence_source': confluence_retriever,
                'origin': RunnablePassthrough() }
            | consolidate_docs
            | LongContextReorder()
        )
    
        # langchain.chains.history_aware_retriever.create_history_aware_retriever

        # = prompt | llm | StrOutputParser() | retriever
        retriever: Runnable[ContextualizeInput, List[Document]] = create_history_aware_retriever(llm, self.__retriever_gatherer, load_prompt('contextualize', input_type=ContextualizeInput))

        self.__full_chain = (
            retriever
            | qa_prompt
            | llm
            | StrOutputParser()
        )

        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        await agent_executor.ainvoke()

    async def loop(self):
        async for message in self.__client.new_messages():
            if not self.__issue_detector_chain({'chat_history': message}):
                continue