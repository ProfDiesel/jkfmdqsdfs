from sklearn.base import BaseEstimator
from sklearn.cluster import AgglomerativeClustering
from sklearn.experimental import enable_halving_search_cv  # noqa
from sklearn.model_selection import HalvingRandomSearchCV
from sklearn.utils.validation import check_is_fitted
from sklearn.preprocessing import PowerTransformer
from scipy.stats import randint, uniform
from dataclasses import dataclass, replace
from sklearn.metrics import fowlkes_mallows_score

from numpy import ndarray

class SparseMatrix:
    presence: ndarray[bool]
    values: ndarray[float]

@dataclass
class Similarity:
    semantic: ndarray
    lexical: ndarray
    social: ndarray
    time: ndarray
    perplexity: SparseMatrix

class Case:
    messages: list[Message]
    metrics: list[Metrics]
    elser_tokens: list[Token]
    similarity: Similarity
    labels: list[int]
    nb_threads: int # = len(set(labels))


# for each group, proportion of threads started by this group
# def compute_orientation(cases: Collection[Case]) -> Mapping[Goup, float]:
#     result: dict[Group, int] = {group: 0 for group in groups.values()}
#     nb_threads: int = 0
#     for case in cases:
#         creators: dict[int, Group] = {}
#         for message, label in zip(case.messages, case.labels):
#             if label not in creators:
#                 creators[label] = groups[message.author]
#         for group in creators.values():
#             result[group] += 1
#         nb_threads += len(creators)
#     return {group: nb / nb_threads for group, nb in result.items()}

# pour chaque thread, proportion des membres de chaque groupe
# for chaque pair de groupe, 
#def compute_social_similarity(cases: Collection[Case]):

#def compute_token_frequency(cases: Collection[Case]) -> Mapping[Token, float]:
#    result: dict[Token, float] = {}
#    for case in cases:
#        for token, weight in zip(case.elser_tokens, case.metrics.lexical):
#            result[token] = result.get(token, 0) + weight
#    return result

def onset_correlation(similarity_metric: ndarray, labels: list[int]):
==> afficher la distance avec le précédent

class CompositeDistanceFeature:
    def __init__(self, semantic_weight: float, lexical_weight: float, time_weight: float, social_weight: float, perplexity_weight: float):
        self.semantic_weight = semantic_weight
        self.lexical_weight = lexical_weight
        self.time_weight = time_weight
        self.social_weight = social_weight
        self.perplexity_weight = perplexity_weight

    def transform(self, X: Sequence[Similarity]):
        similarity: Similarity
        for similarity in X:
            composite = (1 + self.semantic_weight * similarity.semantic) * (1 + self.lexical_weight * similarity.lexical) \
                      * (1 + self.time_weight * similarity.time) * (1 + self.social_weight * similarity.social)
            for i in len(composite):
                for j in len(composite):
                    similarity.perplexity
        return cols

    def fit(self, X, y=None):
        return self


class TemplateEstimator(BaseEstimator):
    def __init__(self, linkage: str, semantic_weight: float, lexical_weight: float, time_weight: float, social_weight: float, perplexity_weight: float):
        pass

    def fit(self, X, y):
        X, y = self._validate_data(X, y, accept_sparse=True)
        self.is_fitted_ = True
        return self

    def predict(self, X):
        # Check if fit had been called
        check_is_fitted(self)
        # We need to set reset=False because we don't want to overwrite `n_features_in_`
        # `feature_names_in_` but only check that the shape is consistent.
        X = self._validate_data(X, accept_sparse=True, reset=False)

        distances, nb_threads = X
        composite_distance = (distances * ...)
        clustering = AgglomerativeClustering(linkage=self.__linkage, metric="precomputed", n_clusters=nb_threads)
        clustering.fit(composite_distance)
        return clustering.labels_








@dataclass
class ThreadClusteringParams:
    linkage: str
    semantic_weight: float
    lexical_weight: float
    time_weight: float
    social_weight: float
    perplexity_weight: float
    distance_threshold: float = 1

def fit(cases: list[Case], params: ThreadClusteringParams) -> ThreadClusteringParams:
    #
    # I. Fit extraction
    # ===
    # I.A. fit on raw features:
    #  - group orientation
    #  - token frequency
    #  - social footprint
    # I.B. recompute weighted lexical, social, time
    # I.C. recompute similarities 
    # I.D. fit rescaler for similarities, perplexity
    PowerTransformer('box-cox')
    # I.E. compute scaled features
    similarities = []
    distances = []

    labels = [case.labels for case in cases]

    #
    # II. Fit classifier params
    # II.A. fit feature weight
    clf = ClassifierWithThreadHint()
    param_distributions = {"linkage": ['ward', 'average', 'complete', 'single'],
                        "semantic_weight": randint(1, 100),
                        "lexical_weight": randint(1, 100),
                        "time_weight": randint(1, 100),
                        "social_weight": randint(1, 100),
                        "perplexity_weight": randint(1, 100),
                        }
    search = HalvingRandomSearchCV(clf, param_distributions, 
                                   scoring=fowlkes_mallows_score,
                                   resource='n_estimators', max_resources=10, random_state=0)
    search.fit([(distances, case.nb_threads) for similarity, case in zip(distances, cases)], labels)
    params = replace(params, **search.best_params_)

    # II.B fit distance threshold
    clf = ClassifierWithThreadHint(params)
    param_distributions = {"distance_threshold": uniform(loc=100, scale=100)}
    search = HalvingRandomSearchCV(clf, param_distributions, 
                                   scoring=fowlkes_mallows_score,
                                   resource='n_estimators', max_resources=10, random_state=0)
    search.fit(distances, labels)
    params = replace(params, **search.best_params_)

    return params

