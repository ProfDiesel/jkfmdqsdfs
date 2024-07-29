
Description
============


Terms and Definitions
=====================
Channel: Symphony chat room, Teams meeting / conversation
Datasource: type of input of the system
DatapProd: 

Macro Architecture
==================
C4 diag

For each thread of discussion (there can be several concomitant threads in single channel), a "pack" is instanciated.
A "pack" multi-agent:
Agents ("Rat") are async, scripted behavior. One per DataProd
Data produced by "rats" are consolidated and exposed

GUI: dispays for each thread the relevant info
    + dedicated chat channel to the "pack" of the thread
    + possibility to like / dislike content

Monitoring UI:
- see embeddings
- chunks and how docs are split
- KPIs of the RAG

Micro Architecture
==================
C4 diag

symphony bot
teams bot
wiki




Data
======
For each datasource, following sections: collection, embedding, storage, processing, secu concern

Contextualizer:
---------------
collection: manual list of users, ADES

Chats:
-----
collection: extraction (history), and bots (realtime)
embedding: chunk by room/day/thread (+ 512 tok summary for ELSER) 
storage: in ES, full text, dense & sparse indexing
secu concerns: - nominative data
               - store only summary to limit risk ?


Wiki:
-----
collections: confluence
embedding: unstructured
storage: in ES
secu concern: ELDAP

Jira:
-----
collections: confluence
embedding: description + comments + metadata
storage: in ES
secu concern: ELDAP

App config git:
---------------
generate git commit message for sweeper car
Harper Reed: use LLM to generate meaningfull git commit messages
storage: git

Knowledge base:
---------------
dedicated content, filled by TS
collection: manual
embedding: dense (reverse hyde, from a hypothetical use case)
storage: journalized in git, sqlite rebuilt for every launch

Glossary:
---------
collection: manual
embedding: keywords
storage: journalized in git, sqlite rebuilt for every launch




DataProd:
=========

App logs:
---------
grepped on demand
command line determined from knowledge base


Question:
---------
ask question for further info
determined from knowledge base

Action & Hint:
--------------
determined from knowledge base

Glossary:
---------
used to fill the context
breadth-first with heuristic: Sum((depth_level * nb_sibling)^-1)
==> TF-IDF plutôt (https://en.wikipedia.org/wiki/Tf%E2%80%93idf) ?

Rats
======
Chat rats:
- chat bots that APS members can invite
- diff behavior depending on the members (TS only, TS & users, TS & dev) 


Non-Reg Chain
===============
For latter re-evaluation, all the inputs and outputs of the RAG will be archived in ES
