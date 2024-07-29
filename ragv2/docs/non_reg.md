- for each input event, a unique ID (type of ID + timestamp + UUID) is generated
- this ID will be the "tracker ID" during all the processing chain
- "taps" will dump content to the disk, identified by the tracker ID


Chunk Attribution: A chunk-level boolean metric that measures whether a ‘chunk’ was used to compose the response.
Chunk Utilization: A chunk-level float metric that measures how much of the chunk text that was used to compose the response.
Completeness: A response-level metric measuring how much of the context provided was used to generate a response
Context Adherence: A response-level metric that measures whether the output of the LLM adheres to (or is grounded in) the provided context.

Context Retrieval Evaluation
- Context relevance - How relevant is the context to the question? The context c(q) is consid- ered relevant to the extent that it exclusively contains information that is needed to answer the question. 
- Context recall - Is the context accurate compared to the ground truth data to give an answer?
- Context adherence - Are the generated answers based on the retrieved context and nothing else ?

Once you have a good semantic search process, you can start testing different prompts and models. Here are some frequent evaluation metrics:

Content Generation Evaluation
- Faithfulness We say that the answer as(q) is faithful to the context c(q) if the claims that are made in the answer can be inferred from the context.
               How factually accurate is the answer given the context?
               You can mark an answer as faithful if all the claims that are made in the answer can be inferred from the given context. This can be evaluated on a (0,1) scale, where 1 is high faithfulness
- Answer relevance We say that the answer as(q) is relevant if it directly addresses the question in an appropriate way. 
                   How relevant is the answer to the question at hand?
                   For example, if you ask: “What are the ingredients in a peanut butter and jelly sandwich and how do you make it?" and the answer is "You need peanut butter for a peanut butter and jelly sandwich," this answer would have low relevancy. It only provides part of the needed ingredients and doesn't explain how to make the sandwich.‍
- ‍Correctness: How accurate is the answer against the ground truth data?
- ‍Semantic similarity: How closely does the answer match the context in terms of meaning (semantics)?
