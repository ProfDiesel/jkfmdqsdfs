from __future__ import annotations

from datetime import timedelta

"""
- query elastic JSON
- réponse élastic JSON

- list de doc
    - lien vers elastic
    - différents scores de la recherche
    - nombre de tokens du doc
    - score de RAGAS sur cette recherche, éclaté par document
"""



class Result:
    took: timedelta
    hits: list[Hit]

{
    "took": ...,
    "timed_out" : false,
    "_shards" : {
        "total" : 1,
        "successful" : 1,
        "skipped" : 0,
        "failed" : 0
    },
    "hits" : {
        "total" : {
            "value" : 5,
            "relation" : "eq"
        },
        "max_score" : ...,
        "hits" : [
            {
                "_index" : "example-index",
                "_id" : "3",
                "_score" : 0.8333334,
                "_source" : {
                    "integer" : 1,
                    "vector" : [
                        3
                    ],
                    "text" : "rrf rrf rrf"
                }
            },
            {
                "_index" : "example-index",
                "_id" : "2",
                "_score" : 0.5833334,
                "_source" : {
                    "integer" : 2,
                    "vector" : [
                        4
                    ],
                    "text" : "rrf rrf"
                }
            },
            {
                "_index" : "example-index",
                "_id" : "4",
                "_score" : 0.5,
                "_source" : {
                    "integer" : 2,
                    "text" : "rrf rrf rrf rrf"
                }
            }
        ]
    },
    "aggregations" : {
        "int_count" : {
            "doc_count_error_upper_bound" : 0,
            "sum_other_doc_count" : 0,
            "buckets" : [
                {
                    "key" : 1,
                    "doc_count" : 3
                },
                {
                    "key" : 2,
                    "doc_count" : 2
                }
            ]
        }
    }
}

from dataclasses import dataclass

class Embedding: ...

class ElasticDocId:
    index: str
    id: int

class Doc:
    id: ElasticDocId
    embedding: Embedding

class Score: ...

class Aggregator:
    def telemetry_span(self): ...
    def doc_atribution(docs: list[DocId]): ...
    def 

AGGREGATOR: Aggregator


    

def request_store() -> list[tuple[Doc, Score]]:
    with telemetry_span():
        result = elastic.request()

    return []

def rag():