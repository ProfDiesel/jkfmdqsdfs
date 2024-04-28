from typing import Literal, Final

import orjson
from pydantic.dataclasses import dataclass
from pydantic import TypeAdapter

from ..endpoint import QueryEmbedder 
from .vectorstore import VectorStore, Vector, Score

@dataclass(frozen=True, kw_only=True)
class Comment:
    author: str
    text: str

@dataclass(frozen=True, kw_only=True)
class Jira:
    key: str
    title: str
    kind: Literal['bugfix', 'new feature']
    fix_version: str | None
    text: str
    comments: list[Comment] 

JIRA_ADAPTER: Final[TypeAdapter] = TypeAdapter(Jira)


async def search(store: VectorStore[Jira], embedder: QueryEmbedder, query: str, *, version: str, k: int = 4) -> list[tuple[Jira, Score]]:
    return [(JIRA_ADAPTER.validate_json(payload), distance) for payload, distance in store.connection.execute( f"""
        SELECT payload, distance
        FROM (
            SELECT * FROM {store.table} e
            WHERE ((json_extract(payload, '$.kind') = 'new feature') AND (semver(json_extract(payload, '$.fix_version'), ${version}) < 0))
                OR ((json_extract(payload, '$.kind') = 'bug') AND (semver(json_extract(payload, '$.fix_version'), ${version}) >= 0))
        )
        INNER JOIN vss_{store.table} v on v.rowid = e.rowid  
        WHERE vss_search(v.embedding, vss_search_params('{orjson.dumps(await embedder(query)).decode()}', {k}))
    """)]
