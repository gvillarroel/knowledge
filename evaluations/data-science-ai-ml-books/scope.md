# Data Science, AI, and Machine Learning Books: Scope

## Purpose

This dataset is a private, English-language knowledge corpus derived from 38
EPUB books in two user-provided Google Drive folders. It supports local,
evidence-grounded consultation across data science, data engineering, machine
learning, generative AI, large language models, privacy, SQL, and production
platform architecture.

The two source folders remain separate logical collections:

- `ds`: 20 books focused on data science, data engineering, databases,
  statistics, SQL, privacy, catalogs, lakehouses, and distributed Python; and
- `ai-ml`: 18 books focused on machine learning, generative AI, language
  models, prompts, training data, security, and AI application engineering.

## Competency questions

1. Which statistical, data-engineering, and machine-learning foundations recur
   across the corpus, and where do authors use different assumptions?
2. How do the books compare batch, streaming, lakehouse, mesh, catalog, and
   platform architectures?
3. Which practices are recommended for training data, evaluation, deployment,
   observability, privacy, and security?
4. How do prompt engineering, retrieval, fine-tuning, agents, and foundation
   model application design differ in purpose and trade-offs?
5. Which implementation guidance is tied to a specific product, library,
   service, or publication date and therefore requires freshness checks?
6. What exact book and EPUB spine document supports each synthesized answer?

## Authority and limits

The book text is authoritative only for what its authors and publisher state.
The folder partition, extraction metadata, and ontology are organizational
records, not publisher claims.

Raw EPUBs and extracted full text are copyrighted private inputs. They remain
under ignored `raw/` and `processed/` paths and must not be committed,
published, attached to reports, or exposed to an evaluator without explicit
authorization. Checked-in files contain only compact source metadata, hashes,
workflow code, and corpus structure.

This is a knowledge corpus, not yet an evaluation benchmark. It must not be
added to the canonical Semantic OKF Harbor registry or used for comparative
ranking until a separate question set, cohorts, hidden ground truth, evidence
bindings, and evaluation policy have been authored and validated.
