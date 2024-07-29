{
    "retriever": {
        "rrf": {
            "retrievers": [
                {
                    "knn": {
                        "field": "vector",
                        "query_vector": [1.25, 2, 3.5],
                        "k": 50,
                        "num_candidates": 100
                    }
                },
                {
                    "standard": {
                        "query": {
                            "text_expansion": {
                                "ml.tokens": {
                                    "model_id": "my_elser_model",
                                    "model_text": "What blue shoes are on sale?"
                                }
                            }
                        }
                    }
                }
            ],
            "window_size": 50,
            "rank_constant": 20
        }
    },
    "size": 3,
    "aggs": {
        "int_count": {
            "terms": {
                "field": "integer"
            }
        }
    }
}


{
    "query": {
        "function_score": {
            "functions": [
                {
                    "gauss": {
                        "price": {
                            "origin": "0",
                            "scale": "20"
                        }
                    }
                },
                {
                    "gauss": {
                        "@timestamp": {
                            "origin": "2013-09-17",
                            "scale": "10d",
                            "offset": "5d",
                            "decay": 0.5
                        }
                    }
                }
            ],
            "query": {
                "bool": {
                    "must": {
                        "knn": {
                            "field": "image-vector",
                            "query_vector": [-5, 9, -12],
                            "num_candidates": 3
                        }
                    },
                    "filter": {
                        "term": {"file-type": "png"}
                    }
                }
            },
            "score_mode": "multiply",
            "script_score": {
                "script": {
                    "source": "Math.log(2 + doc['my-int'].value)"
                }
            },
        }
    }
}

from elasticsearch import Elasticsearch
from .core.model import Chunk, Embedding

class Client:
    def __init__(self):
        self.es_client = Elasticsearch(
            "https://localhost:9200",
            ssl_assert_fingerprint='AA:BB:CC:3C:A4:99:12:A8:D6:41:B7:A6:52:ED:CA:2E:0E:64:E2:0E:A7:8F:AE:4C:57:0E:4B:A3:00:11:22:33',
            basic_auth=("elastic", "passw0rd")
        )

    def put(self, index: str, chunk: Chunk):
        self.es_client.index(index=index, document=chunk)


    def dense_vector_search(self, index: str, embedding: Embedding):
        query_string = {
            "field": "embedding",
            "query_vector": embedding,
            "k": 1,
            "num_candidates": 100
        }
        return self.es_client.search(index=index, knn=query_string, source_includes=['text', 'doc_id'])
