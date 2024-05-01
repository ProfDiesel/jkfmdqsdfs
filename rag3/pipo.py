State = Union[T, Leave]

def parallel(**kwargs):
    gather(identity(v) if not callable(v) else v for k, v in kwargs)

def build_chain():
    detect = detection_chain(llm)
    features = feature_chain(llm)
    user_ask = user_ask_chain(llm, client)
    context = context_chain(llm)
    retrieve = retriev_chain(llm, embedder)
    advise = advise_chain(llm, client)

    def conditionnal_user_ask(issue):
        if not valid(issue):
            user_ask(issue)
            return Leave()
        return issue

    def chain(message):
        (maybe | detect
               | features
               | conditionnal_user_ask
               | parallel(c = context,
                          issue = identity)
               | retrieve
               | advise)

        