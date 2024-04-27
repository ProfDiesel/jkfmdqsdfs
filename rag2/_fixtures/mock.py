from collections.abc import Iterable
from rag2.endpoint import LLM

def mock_llm(responses: Iterable[str]) -> LLM:
    iterator = iter(responses)
    async def llm(query: str, *, model_name: str = '', max_token: int = 1024) -> str:
        return next(iterator)
    return llm
