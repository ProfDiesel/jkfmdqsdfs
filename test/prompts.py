from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate, PromptVa

contextualize_prompt = PromptTemplate.from_file('templates/question_answer.jinja2', template_format='jinja2')
x: PromptValue = contextualize_prompt.invoke({'contexts': ['pipo', 'lolo']})
x.to_messages()

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
