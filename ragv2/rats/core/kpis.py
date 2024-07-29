===> peut être calculé à la demande, sur la constitution de la dataframe

@dataclass
class Message:
    author: str
    text: str

@dataclass
class ThreadExtractionRecord:
    threads: list[list[Message]]

@dataclass
class RagRecord:
    thread: str
    summary: str
    documents: list[Document]
    context: str
    response: str

async def update_stats(context: str, response: str, documents: list[Document]):
    context_embedding = await embedder(context)
    response_embedding = await embedder(response)

    process_total_utilization = 0
    for document in documents:
        document.kpis.nb_attribution += 1
        utilization = similarity(document.embedding, response_embedding)
        document.kips.total_utilization += utilization
        process_total_utilization += utilization

    process.kpis.completeness.add(process_total_utilization / len(documents))
    process.kpis.adherence.add(similarity(context_embedding, response_embedding))




class AgenticKpi:
    ChatMessage(role="system", content="""You are an expert relevance ranker.
                Given a list of documents and a query, your job is to determine how relevant each document is for answering the query.
                Your output is JSON, which is a list of documents.
                Each document has two fields, content and score.
                relevance_score is from 0.0 to 100.0.
                Higher relevance means higher score."""),
    ChatMessage(role="user", content=f"Query: {query} Docs: {docs}")
    temperature=0



    
def get_chunks_kpis() -> DataFrame:
    """select json_extract(parent.payload, '$.title') as title,
            length(json_extract(parent.payload, '$.text')) as text_length,
            length(json_extract(parent.payload, '$.tokens')) as token_length,
            stat.attributions as nb_attributions,
            sum(stat.utilization) / stat.attributions as utilization
    from chunk
            join document as parent on document.rowid = chunk.parent
            join document_stat as stat on stat.chunk = chunk.rowid
        group by chunk.rowid;
    """

def get_rag_kpis() -> DataFrame:
    """ select length(response_text),
            completeness,
            context_adherence
        from records
    """

    
@dataclass
class ThreadDistincionPostMortem:
    ...

class RagPostMortem:
    ...




Given question, answer and context verify if the context was useful in arriving at the given answer. Give verdict as "1" if useful and "0" if not with json output.""",




