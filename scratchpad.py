from typing import Any, Dict, List, Mapping, Optional, Tuple

from langchain_community.vectorstores.sqlitevss import SQLiteVSS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_core.messages.system import SystemMessage

from jinja2 import Template

from .playground import PlaygroundChatModel, PlaygroundEmbeddings



llm = PlaygroundChatModel(model_name="Youhou")
embeddings = PlaygroundEmbeddings()
jira_vectorstore = SQLiteVSS(table='jiras', connection=None, embedding=embeddings)
chat_vectorstore = SQLiteVSS(table='chat', connection=None, embedding=embeddings)
userguide_vectorstore = SQLiteVSS(table='userguide', connection=None, embedding=embeddings)
confluence_vectorstore = SQLiteVSS(table='confluence', connection=None, embedding=embeddings)
#DocArrayInMemorySearch

jira_retriever = jira_vectorstore.as_retriever()
chat_retriever = chat_vectorstore.as_retriever(search_type='mmr')
userguide_retriever = userguide_vectorstore.as_retriever(search_type='similarity_score_threshold')
confluence_retriever = confluence_vectorstore.as_retriever(search_type='similarity_score_threshold')

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)



contextualize_prompt = PromptTemplate.from_file('', template_format='jinja2')

qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\
Always say "thanks for asking!" at the end of the answer.
"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="system_with_contexts"),
        ("human", "{question}"),
    ]
)

#
# Step 1. Use the LLM to contextualize (chat history) and return a canonical question

contextualize_chain = (
    contextualize_q_prompt
    | llm
    | StrOutputParser()
).with_config(tags=["contextualize_chain"])

#
# Step 2. Rag request

def process_chat_results(docs: List[Document]) -> List[Document]:
    return docs

def consolidate_docs(sources: Mapping[str, List[Document]]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for retriever, docs in sources.items():
        for doc in docs:
            result[retriever] = '\n\n'.join(doc.page_content)
    return result


S'assurer qu'on a bien la config, sinon demander
=> cherche la config dans la base




rag_chain = (
    contextualize_chain
    | { 'jiras_source': jira_retriever,
        'chat_source': chat_retriever | process_chat_results,
        'userguide_source': userguide_retriever,
        'confluence_source': confluence_retriever,
        'origin': RunnablePassthrough() }
    | consolidate_docs
    | qa_prompt
    | llm
    | StrOutputParser()
)

chat_history = [("human", "what's 5 + 2"), ("ai", "5 + 2 is 7")]

rag_chain.bind(chat_history=chat_history).invoke({'question': 'What is Task Decomposition'})

