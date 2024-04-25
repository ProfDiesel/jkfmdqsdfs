from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import AgentExecutor, create_react_agent

from .irc import IRCClient

from typing import Dict, TypedDict, Type, Any, overload, TypeVar, Optional
from langchain_core.runnables import RunnablePassthrough, RunnableBranch, RunnableSerializable, Runnable
from langchain.prompts import PromptTemplate
from langchain_core.prompt_values import PromptValue 
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import BooleanOutputParser
from langchain_core.language_models import BaseLanguageModel
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from langchain.globals import set_verbose, set_debug
set_verbose(True)


InputT = TypeVar('InputT', bound=Dict[str, Any])

@overload
def load_prompt(name: str, *, input_type: Type[InputT]) -> Runnable[InputT, PromptValue]: ...

@overload
def load_prompt(name: str, *, input_type: None) -> Runnable[None, PromptValue]: ...

def load_prompt(name: str, *, input_type: Optional[Type[InputT]]) -> Runnable[InputT | None, PromptValue]:
    return PromptTemplate.from_file(name, template_format='jinja2').with_types(input_type=input_type)

class IssueDetectorInput(TypedDict):
    chat_history: str

class ContextualizeInput(TypedDict):
    chat_history: str

class Engine:
    def __init__(self, client: IRCClient, llm: BaseLanguageModel):
        self.__client = client
        
        self.__issue_detector_chain: Runnable[IssueDetectorInput, bool] = (
            load_prompt('detect_errors', input_type=IssueDetectorInput)
            | llm
            | BooleanOutputParser()
        ).with_config(run_name='issue_detector_chain')

        self.__retriever_gatherer = (
            RunnablePassthrough()
            | { 'jiras_source': jira_retriever,
                'chat_source': chat_retriever | process_chat_results,
                'userguide_source': userguide_retriever,
                'confluence_source': confluence_retriever,
                'origin': RunnablePassthrough() }
            | consolidate_docs
        )

        # = prompt | llm | StrOutputParser() | retriever
        retriever: RunnableSerializable[ContextualizeInput, List[Document]] = create_history_aware_retriever(llm, self.__retriever_gatherer, load_prompt('contextualize', input_type=ContextualizeInput))

        self.__full_chain = (
            retriever
            | qa_prompt
            | llm
            | StrOutputParser()
        )

        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    async def loop(self):
        async for message in self.__client.new_messages():
            if not self.__issue_detector_chain({'chat_history': message}):
                continue