from functools import reduce
from typing import Any, Dict, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import SimpleChatModel 
from langchain_core.messages import BaseMessage, merge_content
from langchain_core.messages.ai import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.outputs import ChatGeneration, ChatResult


class PlaygroundChatModel(SimpleChatModel):
    model_name: str
    max_tokens: int = 1024

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        merged = BaseMessage(reduce(merge_content, (message.content for message in messages)))
        request: str = StrOutputParser().invoke(merged)
        return await lab_magic(request)

    @property
    def _llm_type(self) -> str:
        return "playground-chat-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return { "model_name": self.model_name }


class PlaygroundEmbeddings(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return []

    def embed_query(self, text: str) -> List[float]:
        return []

