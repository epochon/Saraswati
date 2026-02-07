
---

# Project: EpochOn 2.0 – Deliberative Legal & Complaint Assistance System

---

## Goal

To build a **deliberative, multi-agent legal assistance platform** that helps users with:

* Filing legitimate complaints
* Understanding legal rights and procedures
* Exploring topics like marriage laws, consumer rights, and civil protections

The system is designed to **reason before acting**, ensuring responsible autonomy in high-stakes civic and legal contexts.

---

## Problem Statement

### Lack of Trustworthy, Deliberative Legal & Complaint Assistance Under Uncertainty

Users frequently lack clear and reliable guidance for legal procedures—such as complaint filing, marriage registration, or consumer dispute resolution.

Existing AI and digital assistance systems:

* Provide overconfident one-shot answers
* Do not internally deliberate or challenge assumptions
* Cannot explain why a decision was made
* Never pause or refuse when risk or uncertainty is high

This creates significant danger in legal environments, where misinformation or premature action can cause real-world harm.

---

## Key Features

* **Multi-Intent Legal Support**

  * Complaint filing (only when legitimate)
  * Legal knowledge exploration
  * Guided procedural assistance

* **Multi-Agent Deliberation**

  * Advocate Agent (supports user request)
  * Skeptic Agent (challenges validity)
  * Neutral Agent (law-grounded retrieval)
  * Arbiter Agent (final decision authority)

* **Responsible Autonomy**

  * Confidence scoring
  * Risk assessment
  * Refusal and pause logic

* **White-Box Explanations**

  * Visible agent reasoning
  * Evidence sources
  * Decision transparency

* **Interconnected Dialogue**

  * Knowledge → Complaint transitions
  * Complaint → Education fallback
  * Context persistence

* **Step-by-Step Guided UI**

  * Option-based interaction
  * Structured workflows
  * Reduced cognitive overload

* **Multilingual & Voice Ready**

  * Speech-to-text input
  * Multilingual normalization
  * Unified reasoning pipeline

---

## Technical Stack

### Frontend

* Streamlit
* Python UI components
* Step-based interaction flows

### Backend / Orchestration

* LangGraph (multi-agent deliberation graph)
* Python (system orchestration)

### LLM & Reasoning

* Groq (OSS reasoning models – Advocate & Skeptic agents)
* Gemini 2.5 Flash (Arbiter agent, final synthesis)

### Retrieval & Knowledge

* Tavily API (live legal & procedural retrieval)
* File-based legal document corpus (RAG layer)

### Speech & Multimodal

* Groq Whisper (`whisper-large-v3-turbo`) – Speech-to-text
* Multimodal input normalization pipeline

### Memory

* Session-level short-term memory
* Planned long-term deliberation memory

### Configuration & Environment

* `.env` + python-dotenv for API key management

---

## Database

* File-based legal knowledge store
* Vectorization planned for production RAG scaling