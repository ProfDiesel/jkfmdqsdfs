from jinja2 import Environment, PackageLoader, Template
from typing import TypeVar, Type, Callable, Awaitable, Mapping, Final
import orjson
from pydantic import BaseModel

KwargsT = TypeVar('KwargsT', bound=Mapping)

class PromptFactory:
    def __init__(self) -> None:
        self.__environment: Final[Environment] = Environment(loader=PackageLoader('rag', 'templates/prompts'), enable_async=True)

        def schema(output_type: Type[BaseModel]) -> str:
            return orjson.dumps({k: v for k, v in output_type.model_json_schema().items() if k not in {'title', 'type'}}).decode()
        self.__environment.filters['schema'] = schema

    def __getitem__(self, name_and_kwargs_type: tuple[str, Type[KwargsT]]) -> Callable[[KwargsT], Awaitable[str]]:
        name, _ = name_and_kwargs_type
        template: Template = self.__environment.get_template(f'{name}.jinja2')
        async def f(kwargs: KwargsT):
            return await template.render_async(**kwargs)
        return f

prompts = PromptFactory()
