from pydantic import BaseModel, Field

class IssueFeatures(BaseModel):
    """Information about the issue."""
    config_name: str = Field(description="The name of the config")
    reporter: str | None = Field(default=None, description="Name of the person who reported the issue")
