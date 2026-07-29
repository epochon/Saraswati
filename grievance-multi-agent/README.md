---

# EpochOn 2.0 – Deliberative Legal & Complaint Assistance System

> **Theme:** Collective Intelligence Under Uncertainty × Responsible Autonomy

A multi-agent, deliberative AI system that assists users with **legal knowledge** and **complaint filing**, while explicitly reasoning, debating internally, and knowing **when not to act**.

---

## 🧩 Problem Statement

### Lack of Trustworthy, Deliberative Legal & Complaint Assistance Under Uncertainty

Users often lack **clear, reliable guidance** for legal procedures—such as filing complaints, understanding marriage laws, or knowing their consumer and civil rights. Existing AI systems typically:

* Provide overconfident, one-shot answers
* Do not deliberate or challenge assumptions
* Cannot explain *why* a decision was made
* Never refuse or pause when uncertainty is high

This is dangerous in **legal and civic contexts**, where misinformation can cause real harm.

---

## 🧠 Our Solution

### A Unified, Deliberative Multi-Agent Legal Assistance Platform

We build a system that **thinks before acting**.

Instead of a single AI response, multiple agents **debate, challenge, and verify** a user’s request before deciding to:

* Proceed with an action (e.g., file a complaint)
* Educate the user
* Request more information
* Refuse to act when risk is high

---

## 🎯 Key Capabilities

* **Multi-Intent Support**

  * Complaint filing (only if legitimate)
  * Legal knowledge exploration (marriage, rights, procedures)
  * Guided clarification for specific legal topics

* **Multi-Agent Deliberation**

  * Advocate Agent (argues *for* the user)
  * Skeptic Agent (argues *against*, challenges assumptions)
  * Neutral Agent (fact- and law-based via retrieval)
  * Arbiter Agent (final decision-maker)

* **Responsible Autonomy**

  * Confidence and risk scoring
  * Explicit refusal and pause behavior
  * No blind automation

* **White-Box Explanations**

  * Visible agent arguments
  * Confidence and risk scores
  * Transparent decision rationale

* **Interconnected Dialogue**

  * Legal knowledge can evolve into complaints
  * Complaints can fall back into education mode
  * Context preserved across steps

* **Step-by-Step UI**

  * Built with Streamlit
  * Option-based, guided interaction
  * Avoids overwhelming one-shot outputs

* **Multilingual & IVR-Ready**

  * Multilingual text support
  * Voice input via speech-to-text
  * Unified reasoning pipeline

---

## 🏗️ System Architecture

### Agent Orchestration

* **LangGraph** is used to model deliberation as a directed graph:

  * Nodes = Agents
  * Edges = Debate flow
  * Terminal state = Responsible decision

### High-Level Flow

1. User input (text / voice / document)
2. Intent detection & normalization
3. Advocate and Skeptic agents debate
4. Neutral agent provides factual grounding
5. Arbiter agent decides final action
6. System explains *why* it acted or refused

---

## 🧰 Technology Stack

### Agent Orchestration

* **LangGraph** – Explicit multi-agent state and control flow

### LLMs

* **Groq (OpenAI OSS – `gpt-oss-120b`)**

  * Advocate and Skeptic agents
* **Gemini 2.5 Flash**

  * Arbiter agent (final synthesis)

### Speech & Multimodal

* **Groq Whisper (`whisper-large-v3-turbo`)**

  * IVR / voice input
* Multimodal normalization layer

### Knowledge & Retrieval

* **File-based legal documents**
* **Tavily API** for external factual augmentation
  *(Hackathon-safe, fast, reliable)*

### Frontend

* **Streamlit**

  * Step-by-step, option-based UI
  * White-box explanations

### Memory

* Short-term memory (session-level)
* Long-term memory (designed, optional for production)

### Configuration

* `.env` + `python-dotenv` for API keys

---

## 📁 Project Structure

```text
epochon-2.0-deliberative-legal-ai/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── main.py
│   ├── ui/
│   ├── agents/
│   ├── orchestration/
│   ├── memory/
│   ├── rag/
│   ├── multimodal/
│   └── utils/
├── data/
├── demos/
├── docs/
└── evaluation/
```

---

## 🔐 Environment Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
GROQ_WHISPER_API_KEY=your_groq_whisper_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## ▶️ How to Run (Local)

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

> The system is designed for **local execution during the hackathon**.
> Deployment is intentionally not required.

---

## 📊 Observability & Reliability (Design-Level)

* **LangSmith** is planned for tracing multi-agent deliberation
* Every decision path is designed to be inspectable and auditable
* Demonstrates responsible autonomy and refusal logic

---

## 🚀 Deployment (Planned, Not Executed)

* **Demo:** Local Streamlit execution
* **Future:** Streamlit Community Cloud or Docker + Google Cloud Run

---

## 🎯 Why This Matters

* Legal misinformation causes real harm
* Blind automation is unsafe
* Trust requires **deliberation, restraint, and transparency**
* AI systems must know **when not to act**

---

## 🏁 Final One-Liner

> *We build a deliberative, multi-agent legal assistance system that intelligently shifts between knowledge, guidance, and action—while knowing when to pause.*

