from dataclasses import dataclass
from sklearn.metrics.cluster import fowlkes_mallows_score

# explicitly require this experimental feature
from sklearn.experimental import enable_halving_search_cv # noqa
# now you can import normally from model_selection
from sklearn.model_selection import HalvingRandomSearchCV
from sklearn.cluster import AgglomerativeClustering




"""

I. apprendre les ki sur des cas ou l'on connait le nombre de clusters, avec un agglomerative(clusters=n)
II. apprendre le threshold 

temps orienté:
distance plus importante avec les messages précédent quand c'est un trader qui parle

lexical: que du bonus si recoupement ?

embedding => semantic
elser => lexical

elastic: synonyms API
https://www.elastic.co/search-labs/blog/text-expansion-pruning
=> appliquer nos propres synonymes sur les résultats ELSER ?
"""


@dataclass
class Message:
    ...
 
@dataclass
class TestCase:
    messsages: list[Message]
    n_clusters: int
    labels: list[int]

def clusterize(messsages: list[Message]) -> list[int]: ...

def make_dataset(cases: list[TestCase]) -> tuple[list[list[Message]], list[list[int]]]: ...


import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

class ThreadClusteringEstimator(ClassifierMixin, BaseEstimator):
    def __init__(self, **kwargs):
        self.__clustering = AgglomerativeClustering(**kwargs)

    def fit(self, X, y=None):
        self.dummy_ = True
        return self

    def predict(self, X):
        return self.__clustering.fit_predict(X)

    def score(self, X, y):
        predictions = self.predict(X)
        return fowlkes_mallows_score(y, predictions)


clf = ThreadClusteringEstimator()

np.random.seed(0)

param_distributions = {"k_embedding": rand(),
                       "k_semantic": rand(),
                       "k_time": rand(),
                       "k_social": rand(),
                       }

X, y = make_dataset()

search = HalvingRandomSearchCV(clf, param_distributions,
                               resource='n_estimators',
                               max_resources=10,
                               random_state=0).fit(X, y)



from nicegui import ui
@ui.page('/graph', response_timeout=300)
def graph(): ...


from scipy.spatial import distance_matrix