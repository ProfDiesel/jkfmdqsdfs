from typing import Optional
from pydantic import BaseModel, Field
from orjson import dumps


class IssuePerimeter(BaseModel):
    """Information about the perimeter."""
    # ^ Doc-string sent to the LLM

    config_name: Optional[str] = Field(default=None, description="The name of the config")
    version: Optional[str] = Field(default=None, description="The last version running if known")
    client_name: Optional[str] = Field(default=None, description="Client name if known")
    canonical_question: Optional[str] = Field(default=None, description="Standalone question")

print(dumps(IssuePerimeter.model_json_schema()))
_PYDANTIC_FORMAT_INSTRUCTIONS = """The output should be formatted as a JSON instance that conforms to the JSON schema below.
