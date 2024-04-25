from typing import Any, Dict, Optional, Type, TypeVar, overload

from langchain.prompts import PromptTemplate
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable

InputT = TypeVar('InputT', bound=Dict[str, Any])

def load_prompt(name: str, *, input_type: Type[InputT]) -> Runnable[InputT, PromptValue]:
    return PromptTemplate.from_file(name, template_format='jinja2').with_types(input_type=input_type)

#@overload
#def load_prompt(name: str, *, input_type: None) -> Runnable[None, PromptValue]: ...

#def load_prompt(name: str, *, input_type: Optional[Type[InputT]]) -> Runnable[InputT | None, PromptValue]:
#    return PromptTemplate.from_file(name, template_format='jinja2').with_types(input_type=input_type)
