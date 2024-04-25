from dataclasses import dataclass
import sqlite3
from pathlib import Path
from sqlite3 import Connection
from typing import Final, List, Tuple, Literal
from jinja2 import Template

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

class JiraEmbedder:
    def __init__(self, db_file: Path, table: str, embeddings: Embeddings):
        self.__vectorstore: Final[SQLiteVSS] = SQLiteVSS(table=table, connection=None, embedding=embeddings)
        self.__template: Final[Template]

    def __make_document(self, jira: Jira) -> Document:
        return Document(page_content=self.__template.render(jira=jira), metadata={'key': jira.key, 'title': jira.title, 'kind': jira.kind, 'fix_version':jira.fix_version})

    def add_jira(self, jiras: List[Jira]) -> List[str]:
        return self.__vectorstore.add_documents([self.__make_document(jira) for jira in jiras])


class JiraTool(BaseTool):
    def __init__(self, db_file: Path, table: str, embeddings: Embeddings):
        self.__connection: Final[Connection] = sqlite3.connect(str(db_file))
        self.__connection.enable_load_extension(True)
        sqlite_vss.load(self.__connection)
        sqlite_semver.load(self.__connection)
        self.__table: Final[str] = table

        self.__embeddings: Final[Embeddings] = embeddings


    def invoke(self, query: str, *, min_version: str = '', k: int = 4, min_score: float = 0) -> List[Tuple[Document, float]]:
        embedding = self.__embeddings.embed_query(query)
        sql_query = f"""
            SELECT text, metadata, distance
            FROM (
                SELECT * FROM {self.__table} e
                WHERE semver(json_extract(metadata, '$.version'), ${min_version}) >= 0
            )
            INNER JOIN vss_{self.__table} v on v.rowid = e.rowid  
            WHERE vss_search(v.text_embedding, vss_search_params('{orjson.dumps(embedding).decode()}', {k}))
        """

        return [(Document(page_content=text, metadata=orjson.loads(metadata) or {}), distance) for text, metadata, distance in self.__connection.execute(sql_query)]
