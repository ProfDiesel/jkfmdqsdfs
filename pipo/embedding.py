# https://huggingface.co/blog/embedding-quantization
# https://sbert.net/docs/package_reference/quantization.html
# https://unum-cloud.github.io/usearch/sqlite/index.html#bit-vectors
from sentence_transformers.quantization import quantize_embeddings
embeddings = model.encode(["I am driving to the lake.", "It is a beautiful day."])
int8_embeddings = quantize_embeddings(
    embeddings,
    precision="int8",
    calibration_embeddings=calibration_embeddings,
)

template = """
You are an intelligent assistant.
Your task is to answer the following multiple-choice questions.
Think step-by-step through the problem to ensure you have the correct answer.
Then, answer the question using the following format 'Action: Answer("[choice]")'  
The parameter [choice] is the letter or number of the answer you want to select (e.g. "A", "B", "C", or "D")
For example, 'Answer("C")' will select choice "C" as the best answer.
You MUST select one of the available choices; the answer CANNOT be "None of the Above".
Be concise.

"""


"""
using tools:
ADES
grep in logs 10 lines around the Error
"""

CLASSIFICATION_PROMPT = f"""You will be given a list of chat messages.
Your task to do find out which message the last message (last_message) is a reply to.
Return the message id of the message that the last_message is a reply to
ONLY OUTPUT THE MESSAGE ID OF THE MESSAGE THAT THE LAST MESSAGE IS A REPLY TO.
IF THE LAST MESSAGE IS NOT A REPLY TO ANY OTHER MESSAGE RETURN 0
OUTPUT ONLY THE ID NUMBER OR NUMBER 0
Discord Message:
{discord_messages}


Last_message:
{last_message}


The last message (last_message) is a reply to message id:
"""


# https://www.rungalileo.io/blog/mastering-rag-improve-performance-with-4-powerful-metrics#rag-evaluation


"""
Chunk Attribution: A chunk-level boolean metric that measures whether a ‘chunk’ was used to compose the response.
Chunk Utilization: A chunk-level float metric that measures how much of the chunk text that was used to compose the response.
Completeness: A response-level metric measuring how much of the context provided was used to generate a response
Context Adherence: A response-level metric that measures whether the output of the LLM adheres to (or is grounded in) the provided context.
"""

"""
- Faithfulness We say that the answer as(q) is faithful to the context c(q) if the claims that are made in the answer can be inferred from the context.
- Answer relevance We say that the answer as(q) is relevant if it directly addresses the question in an appropriate way. 
- Context relevance The context c(q) is consid- ered relevant to the extent that it exclusively contains information that is needed to answer the question. 
- Context recall

"""

ChatMessage(role="system", content="You are an expert relevance ranker. Given a list of documents and a query, your job is to determine how relevant each document is for answering the query. Your output is JSON, which is a list of documents.  Each document has two fields, content and score.  relevance_score is from 0.0 to 100.0. Higher relevance means higher score."),
      ChatMessage(role="user", content=f"Query: {query} Docs: {docs}")
temperature=0


def chain():
    query: str
    context: list[Document]
    response: str
    json_dumps(query, context, response)

@dataclass
class DocumentMetrics:
    attribution: int
    utilization: float

@dataclass
class ResponseMetrics:
    completeness: float
    context_adherence: float

Document = int
def stats(context: str, response: str, documents: list[Document]):
    context_embedding = embed(context)
    response_embedding = embed(response)

    for document in documents:
        attribution[document] += 1
        utilization[document] += similarity(document.embedding, response_embedding)

    completeness.add(sum(utilization[doc] for doc in documents) / len(documents))
    adherence.add(similarity(context_embedding, response_embedding))


longueur des chunks => recursive 200, overlap 50
top-k => 20 à 15



Context Retrieval Evaluation

To evaluate which retrieval setup produces the best results, you can use the following evaluators:

    Context relevance - How relevant is the context to the question?
    Context adherence - Are the generated answers based on the retrieved context and nothing else ?
    Context recall - Is the context accurate compared to the ground truth data to give an answer?

Content Generation Evaluation

Once you have a good semantic search process, you can start testing different prompts and models. Here are some frequent evaluation metrics:

    Answer Relevancy: How relevant is the answer to the question at hand?
    For example, if you ask: “What are the ingredients in a peanut butter and jelly sandwich and how do you make it?" and the answer is "You need peanut butter for a peanut butter and jelly sandwich," this answer would have low relevancy. It only provides part of the needed ingredients and doesn't explain how to make the sandwich.‍
    Faithfulness: How factually accurate is the answer given the context?
    You can mark an answer as faithful if all the claims that are made in the answer can be inferred from the given context. This can be evaluated on a (0,1) scale, where 1 is high faithfulness
    ‍Correctness: How accurate is the answer against the ground truth data?
    ‍Semantic similarity: How closely does the answer match the context in terms of meaning (semantics)?



RAG_PROMPT_TEMPLATE = """
<|system|>
Using the information contained in the context,
give a comprehensive answer to the question.
Respond only to the question asked, response should be concise and relevant to the question.
Provide the number of the source document when relevant.
If the answer cannot be deduced from the context, do not give an answer.</s>
<|user|>
Context:
{context}
---
Now here is the question you need to answer.

Question: {question}
</s>
<|assistant|>
"""


Given question, answer and context verify if the context was useful in arriving at the given answer. Give verdict as "1" if useful and "0" if not with json output.""",
