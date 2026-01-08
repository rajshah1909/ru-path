# RU-PATH — AI-Powered Campus Parking & Transit Assistant

RU-PATH is an AI system that answers natural-language questions about parking eligibility, bus routing, and building navigation across Rutgers University–New Brunswick.  
The system is designed to **ground LLM responses in official institutional data**, enforce deterministic rules, and support multi-turn, constraint-aware reasoning.

This project emphasizes **system design, reliability, and evaluation**, not just language generation.

---

## Problem

Rutgers University–New Brunswick spans multiple campuses with complex, time-dependent parking rules and overlapping bus routes. Students and visitors frequently struggle to answer questions such as:

- Where can I legally park near a specific building with my permit?
- Which bus route should I take between campuses?
- What is the closest bus stop to my destination?
- Do parking rules change after a certain time?

Existing resources are fragmented across static websites, PDFs, and maps, with no unified, interactive interface. As a result, users waste time, take inefficient routes, or violate parking regulations.

---

## Constraints & Reality

The system had to operate under real-world constraints:

- **Ambiguous user queries** (e.g., “Where can I park near Hill Center?”)
- **Multiple campuses and permit types** with time-based rules
- **Static but authoritative data** from official Rutgers sources
- **LLM hallucination risk** when answering regulatory questions
- **Multi-turn conversations**, where follow-up questions depend on prior context
- **Low-latency responses** suitable for interactive use

These constraints strongly influenced the final architecture.

---
# RU-PATH — AI-Powered Campus Parking & Transit Assistant

▶️ **Demo Video:** https://youtu.be/XkFiByMFBlc

RU-PATH is an AI system that answers natural-language questions about parking eligibility, bus routing, and building navigation across Rutgers University–New Brunswick.  
The system is designed to **ground LLM responses in official institutional data**, enforce deterministic rules, and support multi-turn, constraint-aware reasoning.

---
## Key Design Decisions

### Deterministic Rule Enforcement
Official Rutgers parking and transit policies were normalized into structured JSON and treated as the **single source of truth**.  
Eligibility decisions (permit type, campus, time window) are computed deterministically rather than delegated to the LLM.

### Hybrid Reasoning (Rules + LLM)
- Rule-based filtering and validation enforce correctness.
- The LLM is used for **language understanding, explanation, and dialogue flow**, not rule enforcement.

This separation significantly reduces hallucinations while preserving conversational flexibility.

### Retrieval-Augmented Generation (RAG)
- User queries and campus documents are embedded.
- Only relevant, validated context is retrieved.
- The LLM is constrained to respond using retrieved information only.

### Explicit Clarification for Ambiguity
When user intent is underspecified, the system asks targeted follow-up questions rather than guessing, improving correctness in multi-turn interactions.

### Modular Pipeline
The system is structured as:

Data → Retrieval → Constraint Validation → Ranking → Response Generation

This design improves debuggability, evaluation, and extensibility.

---

## System Architecture

### Data Layer
Manually curated datasets derived from **official Rutgers sources**, stored as structured JSON:
- Parking lots with permit eligibility and time rules
- Bus routes and stops
- Campus buildings and locations

All datasets are normalized to a consistent schema.

### Retrieval Layer
- Campus data is embedded and indexed
- User queries are embedded at runtime
- Semantic similarity retrieves relevant context only

### Reasoning & Generation
- Deterministic constraint checks applied before generation
- DeepSeek API used for natural-language interpretation and response generation
- Session-based memory maintains multi-turn conversation context

### Backend & Deployment
- Flask REST API
- Modular services for retrieval, reasoning, and dialogue state
- Dockerized deployment
- CI/CD via GitHub Actions
- Hosted on Render

---

## Results & Evaluation

- Built a structured evaluation set of real campus queries covering parking eligibility, bus routing, and building navigation.
- Achieved **maximum achievable accuracy on parking eligibility queries within the defined evaluation set** by enforcing deterministic rule validation using official Rutgers policies encoded as JSON.
- The LLM (DeepSeek API) is used strictly for explanation and conversational flow; all eligibility decisions are validated programmatically.
- Ambiguous queries trigger clarification prompts rather than assumptions, improving reliability in real-world usage.

---

## Reliability & Safety Approach

- Official Rutgers policy data is treated as the single source of truth.
- Eligibility logic is enforced deterministically; the LLM does not decide rules.
- Responses are constrained to retrieved and validated context only.
- This design eliminates hallucinations for rule-based queries while maintaining conversational usability.

---

## What I’d Improve Next

- Integrate live bus tracking and service alerts
- Add automated evaluation and regression testing harness
- Improve retrieval with hybrid keyword + vector search
- Introduce monitoring and user feedback loops
- Expand support to mobile-friendly interfaces

---

## Tech Stack

Python, Flask, DeepSeek API, Vector Embeddings, Docker, GitHub Actions, Render

---
