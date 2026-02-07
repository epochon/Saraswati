# Saraswati

# **AI-Based Multi-Agent Grievance Redressal System (India)**

---

## **1. Introduction**

Public grievance redressal systems in India often suffer from poor complaint quality, lack of legal awareness, and incomplete submissions. Citizens frequently fail to include essential facts, legal grounds, or supporting evidence, resulting in delayed or rejected complaints.

This project proposes an **AI-powered Multi-Agent Grievance Redressal System** that assists users in drafting **legally structured, submission-ready grievances** using a controlled adversarial debate between multiple AI agents. The system guides users from an informal grievance description to a concise portal-ready summary and a detailed legal report.

---

## **2. Problem Statement**

* Citizens lack legal expertise to draft effective grievances.
* Online grievance portals require concise, factual complaints.
* Legal rights and applicable laws are often unknown to users.
* Existing AI systems provide generic responses without structured validation.
* No mechanism exists to **challenge, score, and strengthen** a complaint before submission.

---

## **3. Objectives**

* To design an AI system that **analyzes grievances through structured debate**
* To validate grievances against **Indian statutory law**
* To generate:

  * A **short complaint summary** suitable for online portals
  * A **detailed legal report** for records and follow-up
* To provide transparency through **multi-round reasoning**
* To demonstrate a **commercially scalable AI grievance prototype**

---

## **4. System Architecture**

### **4.1 High-Level Flow**

1. User submits grievance text
2. Intake validation checks mandatory fields
3. Multi-agent debate is executed:

   * Advocate
   * Opposition
   * Rebuttals
   * Legal validation
4. Structurer agent produces final outputs
5. User:

   * Copies summary for portal submission
   * Downloads detailed PDF report

---

### **4.2 Multi-Agent Design**

| Agent               | Role                                                    |
| ------------------- | ------------------------------------------------------- |
| Advocate Agent      | Argues in favor of the user (5 strong points + actions) |
| Opposition Agent    | Challenges the complaint (5 weaknesses + corrections)   |
| Rebuttal Agents     | Counter-arguments from both sides                       |
| Legal Advisor Agent | Applies Indian law and assigns legal strength           |
| Structurer Agent    | Produces structured outputs (summary + report)          |

---

## **5. Key Features**

### **5.1 Adversarial Reasoning**

* Arguments are debated instead of blindly accepted
* Prevents weak or speculative claims

### **5.2 Legal Validation**

* Applies Indian statutes such as:

  * Consumer Protection Act, 2019
  * Electricity Act, 2003
  * State Electricity Supply Codes
* Identifies strengths and weaknesses

### **5.3 Dual Output Generation**

* **Short Complaint Summary**

  * Plain language
  * Website-ready
  * Copy-paste friendly
* **Detailed Legal Report**

  * Markdown formatted
  * Evidence checklist
  * PDF export

### **5.4 Transparency**

* Live progress tracking per round
* Agent outputs displayed clearly
* No hidden reasoning

---

## **6. Technology Stack**

### **6.1 Frontend**

* **Streamlit** – Interactive web UI

### **6.2 Backend**

* **Python**
* **Groq LLM API** (fast inference)

### **6.3 AI Orchestration**

* Prompt-driven agent architecture
* JSON-based agent communication

### **6.4 PDF Generation**

* **ReportLab**
* Custom Markdown-aware formatting

---

## **7. Project Structure**

```
grievance-multi-agent/
│
├── app.py
├── orchestrator.py
├── prompts/
│   ├── advocate.txt
│   ├── opposition.txt
│   ├── legal.txt
│   ├── structurer.txt
│
├── agents/
│   ├── advocate.py
│   ├── opposition.py
│   ├── advocate_rebuttal.py
│   ├── opposition_rebuttal.py
│   ├── legal_advisor.py
│   ├── structurer.py
│
├── utils/
│   ├── intake.py
│   ├── json_utils.py
│   ├── render.py
│   ├── pdf.py
│   ├── state.py
│
├── .env
└── requirements.txt
```

---

## **8. Intake Validation Logic**

Mandatory information:

* Name
* Location
* Event description
* Responsible authority
* Impact

If missing → user is prompted before analysis.

---

## **9. Legal Strength Evaluation**

Each grievance receives:

* **Legal Strength Rating**: High / Medium / Low
* **Confidence Meter** (0–100)
* Identified weaknesses
* Actionable steps to strengthen the case

---

## **10. Output Formats**

### **10.1 Short Complaint Summary**

* Used for online grievance portals
* Concise, factual, neutral tone

### **10.2 Detailed Legal Report**

Includes:

* Legal strength analysis
* Draft complaint
* Applicable laws
* Weaknesses
* Evidence checklist
* Strengthening guidance

---

## **11. PDF Generation**

* Converts Markdown legal report into professional PDF
* Supports:

  * Headings
  * Bullet lists
  * Paragraph spacing
* Exported as:
  **AI_Grievance_Complaint.pdf**

---

## **12. External Portal Integration (Prototype)**

* Opens local filing website
* User copies short summary
* Demonstrates real-world submission workflow
* Avoids unsafe browser automation

---

## **13. Security & Ethics**

* No automatic filing without user consent
* Human-in-the-loop design
* No personal data stored
* Transparent reasoning
* No legal advice substitution disclaimer

---

## **14. Limitations**

* Depends on LLM accuracy
* Not a substitute for licensed legal counsel
* Portal autofill is manual (by design)
* State-specific laws may require updates

---

## **15. Future Enhancements**

* Multi-language support (Hindi, Kannada)
* Authority-specific complaint formats
* API-based portal submission
* Evidence upload integration
* Complaint status tracking
* Mobile application version

---

## **16. Conclusion**

The **AI-Based Multi-Agent Grievance Redressal System** demonstrates how adversarial AI reasoning can significantly improve complaint quality, legal compliance, and user empowerment. By combining debate, legal validation, and structured output generation, the system bridges the gap between citizens and formal grievance mechanisms.

This project serves as a **scalable prototype** for intelligent public grievance assistance in India.

---

## **17. References**

1. Consumer Protection Act, 2019
2. Electricity Act, 2003
3. State Electricity Supply Codes
4. ReportLab Documentation
5. Streamlit Documentation



