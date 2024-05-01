# https://atlassian-python-api.readthedocs.io
from atlassian import Jira
from atlassian import Confluence

from datasources.jira import Jira as Issue, Comment
from datasource.chat import Chat, Message


# jql = 'project = DEMO AND status NOT IN (Closed, Resolved) ORDER BY issuekey'
def import_jiras(store: VectorStore, url, username, password, jql):
    jira = Jira(url=url, username=username, password=password)
    template = 
    embedder = 

    get_user = lru_cache(jira.user)

    def get_jiras():
        for issue in jira.jql(jql_request)
            user = get_user(issue.reporter)
            jira.issue_get_comments(issue.key)
            yield Issue(key=, title=, kind=, fix_version=, text=, comments = [Comment(author=, text) for comment in issue.comment] )

    store.insert(template, embedder, list(get_jiras))

def import_confluence(store: VectorStore, url, username, password, ):
    confluence = Confluence(url=url, username=username, password=password)
    template = 
    embedder = 
    confluence.get_all_pages_from_space(space, start=0, limit=100, status=None, expand=None, content_type='page')
    store.insert(template, embedder, list(get_pages))

def import_chats(store: VectorStore, ):
    
    @dataclass(frozen=True, kw_only=True)
    class Message:
        timestamp: datetime
        author: str
        message: str

    @dataclass(frozen=True, kw_only=True)
    class Chat:
        date: date
        messages: list[Message] 

