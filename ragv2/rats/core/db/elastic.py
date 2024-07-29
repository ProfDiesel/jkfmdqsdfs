import requests

class ElasticDocumentDatabase:
    def __init__(self, url, auth, index):
        self.__url = url
        self.__auth = auth
        self.__index = index

    async def put(self, documents: list[Document]) -> None:
        response = requests.put(self.__url / 'index', auth=self.__auth, json={index = self.__index, documents = documents})
        response.json()

    async def search(self, query: str) -> list[tuple[Document, Score]]:
        response = requests.get(self.__url / 'search', auth=self.__auth, json={index = self.__index, query=query})
