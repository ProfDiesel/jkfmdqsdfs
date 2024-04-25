from pydantic import BaseModel, Field
from typing import Optional

class Issue(BaseModel):
    """Information about the perimeter."""

    config_name: str = Field(default=None, description="The name of the config")
    version: Optional[str] = Field(default=None, description="The last version running if known")
    reporter: Optional[str] = Field(default=None, description="Name of the client who reported the issue")


Issue.model_validate_json(json_data)
