# RAG And Vector Search

## Plain-English Version

For review-style questions, the system does not ask the model to answer from memory. It retrieves relevant guest review snippets from a vector database, summarizes the best evidence, and then uses that evidence to generate the answer.

Repo anchors:

- runtime retrieval: [`agent/vector_qdrant.py`](../../agent/vector_qdrant.py)
- vector rebuild / ingestion: [`scripts/rebuild_review_vectors.py`](../../scripts/rebuild_review_vectors.py)
- hybrid route entry: [`agent/graph.py::_exec_rag_node`](../../agent/graph.py)

## What A Vector Database Is In This Repo

A vector database stores numeric vectors instead of only ordinary rows and columns. In this repo, those vectors represent the meaning of review text.

In practice, Qdrant stores:

- one vector per review comment
- payload metadata like listing ID, borough, month, year, sentiment, and `is_highbury`

Repo evidence:

- client and search logic: [`agent/vector_qdrant.py`](../../agent/vector_qdrant.py)
- collection rebuild: [`scripts/rebuild_review_vectors.py`](../../scripts/rebuild_review_vectors.py)

## What An Embedding Is Here

An embedding is a dense numeric representation of text. In this repo, review text and user queries are embedded using:

- `sentence-transformers/all-MiniLM-L6-v2`

Repo evidence:

- model constant `MODEL_NAME` in [`scripts/rebuild_review_vectors.py`](../../scripts/rebuild_review_vectors.py)
- runtime model load in [`agent/vector_qdrant.py::_load_resources`](../../agent/vector_qdrant.py)

Why embeddings matter:

- keyword search would miss paraphrases
- embeddings support semantic retrieval such as:
  - “dirty”
  - “unclean”
  - “cleanliness issue”

all retrieving related reviews even if the wording differs

## Data Source For RAG

The source dataset used for vector rebuild is:

- [`data/clean/review_sentiment_scores.parquet`](../../data/clean/review_sentiment_scores.parquet)

That is loaded in [`scripts/rebuild_review_vectors.py::_load_and_prepare_metadata`](../../scripts/rebuild_review_vectors.py).

Required columns include:

- `comment_id`
- `listing_id`
- `comments`
- `year`
- `month`
- `neighbourhood`
- `neighbourhood_group`
- `is_highbury`
- sentiment scores and `sentiment_label`

## How Chunking Is Done

Chunking in the current repo is simple:

- one review comment = one vectorized chunk

Evidence:

- [`scripts/rebuild_review_vectors.py::_encode_comments`](../../scripts/rebuild_review_vectors.py) encodes `metadata["comments"].tolist()`
- Qdrant point IDs are built per `comment_id`

So the current chunking strategy is:

- chunk boundary: review row boundary
- overlap: none
- semantic segmentation: none
- sentence splitting: none

### Why this choice likely exists

- Airbnb reviews are relatively short
- one-review-per-hit keeps citations and metadata alignment simple
- implementation complexity stays low

### Limitation

- long reviews can mix multiple themes into one vector
- there is no sentence-level precision

## What Metadata Is Stored

Points uploaded to Qdrant in [`scripts/rebuild_review_vectors.py::_upload_batches`](../../scripts/rebuild_review_vectors.py) contain payload fields such as:

- `listing_id`
- `comment_id`
- `comments`
- `year`
- `month`
- `neighbourhood`
- `neighbourhood_group`
- `is_highbury`
- `negative`
- `neutral`
- `positive`
- `compound`
- `sentiment_label`

This is important because retrieval here is not purely semantic. It is semantic retrieval plus structured filtering.

## How The Vector Store Is Structured

The rebuild script:

1. loads and normalizes review rows
2. encodes each comment into a 384-dim embedding
3. saves embeddings and metadata artifacts
4. recreates the Qdrant collection
5. uploads points in batches

Repo anchors:

- [`scripts/rebuild_review_vectors.py::main`](../../scripts/rebuild_review_vectors.py)
- [`scripts/rebuild_review_vectors.py::_recreate_collection`](../../scripts/rebuild_review_vectors.py)
- [`scripts/rebuild_review_vectors.py::_upload_batches`](../../scripts/rebuild_review_vectors.py)

The collection uses cosine distance.

## How Retrieval Works At Runtime

Runtime retrieval begins in [`agent/vector_qdrant.py::exec_rag`](../../agent/vector_qdrant.py).

High-level flow:

1. load Qdrant client, metadata, and embedding model
2. normalize filters
3. infer metadata filters from query and state
4. embed the query
5. search Qdrant
6. apply metadata filters
7. optionally relax date filters if nothing is found
8. convert points into normalized hits
9. rerank hits
10. summarize and dedupe evidence

## How Filters Work

Structured filter construction happens in [`agent/vector_qdrant.py::_build_filter`](../../agent/vector_qdrant.py).

Supported filters include:

- `year`
- `month`
- `borough` / `neighbourhood_group`
- `neighbourhood`
- `listing_id`
- `comment_id`
- `is_highbury`
- `sentiment_label`
- numeric sentiment ranges

Why this matters:

- semantic similarity alone is not enough for analytics-style questions
- users often mean “the right theme in the right location/time scope”

## How Retrieval Hits Are Shaped

Qdrant hits are normalized in [`agent/vector_qdrant.py::_points_to_hits`](../../agent/vector_qdrant.py).

Important normalized fields:

- `listing_id`
- `comment_id`
- `borough`
- `neighbourhood`
- `month`
- `year`
- `snippet`
- `score`
- `is_highbury`
- sentiment fields

This normalized format is what later reranking and summarization consume.

## How Summaries And Citations Are Built

After retrieval, [`agent/vector_qdrant.py::summarize_hits`](../../agent/vector_qdrant.py):

- de-duplicates hits on `(listing_id, comment_id)`
- computes `evidence_count`
- assigns a confidence label such as:
  - `weak`
  - `mixed`
  - `positive`
  - `negative`
  - `neutral`
- creates citations like `listing_id:comment_id`
- creates a short retrieval summary

If no hits are found, it explicitly returns:

- summary = `"No relevant reviews found for the current filters."`
- `weak_evidence = True`

## How The Final Generation Uses Retrieved Context

RAG results do not directly become the final answer. They are passed through the graph into `result_bundle`, then the composer uses:

- review summary
- snippet list
- sentiment cues
- policy and filters

Repo anchors:

- [`agent/graph.py::_exec_rag_node`](../../agent/graph.py)
- [`agent/graph.py::_compose_node`](../../agent/graph.py)
- [`agent/compose.py::compose_answer`](../../agent/compose.py)

## How Semantic Retrieval Differs From Keyword Retrieval

### In plain English

Keyword retrieval matches literal words. Semantic retrieval matches meaning.

### In this repo

The query embedding is compared to review embeddings in vector space, so semantically similar text can match even if exact tokens differ.

This is why:

- “guests complained about dirt”
- “cleanliness issues”
- “unclean apartment”

can all map to similar evidence, even with different vocabulary.

## Why This Repo Chose Its Current RAG Stack

Current stack:

- Qdrant for vector search
- SentenceTransformer for local embeddings
- metadata-aware filtering
- custom reranker

Likely reasons:

- fully local / repo-contained
- cheap to run
- simple to rebuild
- easier to demo than a cloud-first stack

## Alternatives That Were Possible

| Current choice | Alternative | Tradeoff |
| --- | --- | --- |
| Qdrant | Azure AI Search, pgvector, Chroma | Qdrant is easy locally, but enterprise stacks may offer richer ops/features |
| MiniLM embeddings | OpenAI embeddings, E5, BGE | stronger models may improve recall but add cost or complexity |
| review-level chunks | sentence/window chunks | current design is simpler, but less precise |
| custom reranker | cross-encoder reranker | current design is cheaper, but weaker |

## Failure Modes To Be Honest About

- right evidence exists but is not retrieved
- retrieved evidence is thematically close but not the best evidence
- wrong location or date slice
- weak evidence summarized too broadly
- review-level chunking blurs multiple themes into one hit

## Most Meaningful Improvements

1. sentence/window chunking
2. cross-encoder reranker
3. better retrieval diagnostics such as precision@k and reranker lift
4. stronger temporal weighting
5. sentence-level grounding from answer sentences back to snippets

