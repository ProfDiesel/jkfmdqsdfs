from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable
import orjson

from .prompts import PromptLike

class IssueFeatures(BaseModel):
    """Information about the issue."""
    config_name: str = Field(description="The name of the config")
    reporter: Optional[str] = Field(default=None, description="Name of the person who reported the issue")

def create_issue_extractor(prompt: PromptLike, llm: BaseLanguageModel) -> Runnable[dict, IssueFeatures]:
    def schema(output_type: Type[BaseModel]) -> str:
        return orjson.dumps({k: v for k, v in output_type.model_json_schema().items() if k not in {'title', 'type'}}).decode()

    return (
          prompt.bind(output_type=schema(IssueFeatures))
        | llm
        | IssueFeatures.model_validate_json
    ).with_config(run_name='issue_extractor_chain')
