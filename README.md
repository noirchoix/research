# Research Assistant & Prompt Engineering Platform

A full-stack research productivity system that combines persistent document workflows, multi-format generation, scholarly discovery, concurrent text-to-speech, and a deterministic prompt-engineering/evaluation subsystem. The strongest hidden engineering is its inspectable prompt scoring, regression-case generation, failure analysis, and persisted job lineage.

## Engineering profile

This repository demonstrates:

- SQLAlchemy persistence for source documents and generated jobs
- PDF/Word ingestion plus TXT, DOCX, LaTeX, and PDF output generation
- Scholar/SerpAPI research discovery integration
- ElevenLabs TTS with bounded chunking, async semaphore control, and ffmpeg composition
- Prompt-pattern catalogue, framework inference/blending, deterministic synthesis, and heuristic scoring
- Evaluation-suite JSON, scoring rubrics, failure-analysis artifacts, and regression scenarios
- Provider-backed LLM workflows with persisted prompts/results

## Reliability and scope

The architecture is broad, but automated tests/CI should be expanded before presenting it as high-assurance production infrastructure. CORS should also be tightened for production instead of wildcard origins with credentials.

## Core Capabilities

### 1. Research Document Processing

* Upload **PDF or Word** research documents
* Extract structured text and metadata
* Generate:

  * Short summaries
  * Long summaries
  * Research-focused summaries
  * Mathematical / logical formulations (LaTeX → PDF)

### 2. Prompt Engineering System

* Interactive **Prompt Builder** UI
* Compose high-quality prompts using:

  * Reusable **prompt patterns** (CSV-driven)
  * User-defined **context tags** (e.g. `<topic>`, `<audience>`, `<rules>`)
* Supports advanced patterns including:

  * Chain-of-Thought
  * ReAct
  * Ask-for-Input
  * Fact-Check List
  * Template, Semantic Filter, Tail Generation, and more
* Prompts are:

  * Automatically generated
  * Scored against quality heuristics
  * Saved as reusable `.txt` assets if accepted

### 3. Multi-Model LLM Orchestration

* **Cost-efficient architecture**

  * DeepSeek-backed prompt generation for production reliability
  * Higher-capacity models (DeepSeek) reserved for heavy analysis
* Model-aware controls (temperature, usage profile)
* Caching and reuse where applicable

### 4. Text-to-Speech (TTS)

* Convert generated outputs into **MP3 audio**
* Cached per job to avoid repeated costs
* Designed for long-form reading and review

### 5. Research Discovery

* Automatic retrieval of **related academic articles**
* Powered by Google Scholar via SerpAPI

---

## Architecture Overview

### Backend

* **FastAPI**
* SQLAlchemy (extensible persistence layer)
* Modular services:

  * Document ingestion
  * Prompt pattern enforcement
  * LLM execution
  * Prompt scoring & validation
  * TTS generation

### Frontend

* **SvelteKit + TypeScript**
* Research-focused dashboard UI
* Prompt builder with:

  * Pattern palette
  * Tag-based context authoring
  * Live preview, scoring, and downloads

### Prompt Patterns

* Stored in CSV for:

  * Transparency
  * Auditing
  * Embedding and reuse
* Enforced programmatically (not just descriptive)

---

## Design Principles

* **Separation of concerns**: UI, orchestration, prompt logic, and model calls are cleanly isolated
* **Cost awareness**: expensive models used only where justified
* **Reproducibility**: prompts are versionable, exportable artifacts
* **Extensibility**: new patterns, models, or outputs can be added without refactoring core logic

---

## Intended Use Cases

* Technical paper summary (text + audio)
* Proof encoding of complex papers for veracity querying 
* Technical writing
* Prompt engineering R&D

---

## Status

This project is **actively developed** and designed as a production-ready foundation rather than a demo.
Contributions, extensions, and architectural discussions are welcome.
