from ..datasources.jira import get_elastic, get_jql, get_sqlite

class JiraAgent:
    def __init__(self): ...

    def get(self, query):
        match(self.__config):
            case ElasticConfig as elastic:
                get_elastic(elastic, query)
            case SqliteConfig as sqlite:
                get_sqlite(sqlite, query)
            case JiraConfig as jira:
                get_jql(jira, query)