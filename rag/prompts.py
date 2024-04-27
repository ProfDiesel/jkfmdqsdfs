from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, overload, Mapping, cast

from langchain.prompts import PromptTemplate
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable

InputT = TypeVar('InputT', bound=Mapping[Any, Any])
PromptLike = Runnable[Mapping[Any, Any], PromptValue] 

@overload
def load_prompt(name: str, *, input_type: Type[InputT]) -> Runnable[InputT, PromptValue]: ...

@overload
def load_prompt(name: str, *, input_type: None = None) -> Runnable[Dict[Any, Any], PromptValue]: ...

def load_prompt(name: str, *, input_type: Optional[Type[InputT]] = None) -> Runnable[Mapping[Any, Any], PromptValue]:
    return cast(Runnable[Mapping[Any, Any], PromptValue], PromptTemplate.from_file(Path(__file__).parent / f'templates/prompts/{name}.jinja2', template_format='jinja2'))
