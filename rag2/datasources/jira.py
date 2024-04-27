from dataclasses import dataclass
import sqlite3
from pathlib import Path
from sqlite3 import Connection
from typing import Dict, Final, List, Tuple, Literal
from jinja2 import Template

from langchain_core.runnables import RunnableConfig
import orjson
import sqlite_semver
import sqlite_vss
from langchain_community.vectorstores.sqlitevss import SQLiteVSS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.tools import BaseTool

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
    comments: List[Comment] 

    def as_document(self, template: Template) -> Document:
        return Document(page_content=template.render(jira=self), metadata={'key': self.key, 'title': self.title, 'kind': self.kind, 'fix_version':self.fix_version})

class JiraEmbedder:
    def __init__(self, db_file: Path, table: str, embeddings: Embeddings):
        self.__vectorstore: Final[SQLiteVSS] = SQLiteVSS(table=table, connection=None, embedding=embeddings)
        self.__template: Final[Template]

    def add_jira(self, jiras: List[Jira]) -> List[str]:
        return self.__vectorstore.add_documents([jira.as_document(self.__template) for jira in jiras])


class JiraTool(BaseTool):
    def __init__(self, db_file: Path, table: str, embeddings: Embeddings):
        self.__connection: Final[Connection] = sqlite3.connect(str(db_file))
        self.__connection.enable_load_extension(True)
        sqlite_vss.load(self.__connection)
        sqlite_semver.load(self.__connection)
        self.__table: Final[str] = table

        self.__embeddings: Final[Embeddings] = embeddings

    def invoke(self, input: str | Dict, config: RunnableConfig | None = None, **kwargs: orjson.Any) -> orjson.Any:
        return self.search(query=input['query'], version=input['version'])

    def search(self, query: str, *, version: str = '', k: int = 4, min_score: float = 0) -> List[Tuple[Document, float]]:
        """
            if new feature: take if jira fix_version < app version
            if bugfix: take if jira fix_version >= app version
        """

        embedding = self.__embeddings.embed_query(query)
        sql_query = f"""
            SELECT text, metadata, distance
            FROM (
                SELECT * FROM {self.__table} e
                WHERE ((json_extract(metadata, '$.fix_version') = 'new feature') AND (semver(json_extract(metadata, '$.fix_version'), ${version}) < 0))
                   OR ((json_extract(metadata, '$.fix_version') = 'bug') AND (semver(json_extract(metadata, '$.fix_version'), ${version}) >= 0))
            )
            INNER JOIN vss_{self.__table} v on v.rowid = e.rowid  
            WHERE vss_search(v.text_embedding, vss_search_params('{orjson.dumps(embedding).decode()}', {k}))
        """

        return [(Document(page_content=text, metadata=orjson.loads(metadata) or {}), distance) for text, metadata, distance in self.__connection.execute(sql_query)]
