# Smart Library Renewal Assistant

AI-powered library book renewal system with human-in-the-loop safety gates.

## Features

- ✅ Deterministic eligibility checking (no LLM hallucination on high-stakes decisions)
- ✅ RAG-grounded policy explanations (cited sources for blocked renewals)
- ✅ Human-in-the-loop confirmation gates (patron confirms before database writes)
- ✅ 7 golden evaluation scenarios (100% correctness across 5 operational layers)
- ✅ 210 synthetic loans for scale testing
- ✅ LangTrace telemetry for observability

## System Architecture

**Operational Workflow (5 Layers):**
1. **Detection Layer** — Daily monitor identifies loans due within 0–7 days
2. **Decision Layer** — Deterministic eligibility check (pure Python rules)
3. **Language Layer** — RAG policy retrieval & grounded explanations for ineligible cases
4. **Action Layer** — Execute renewal or halt based on eligibility
5. **Transaction Layer** — Database write with verification and rollback safety

**Key Safety Features:**
- **Human-in-the-Loop Gate** — Patron confirmation required before database writes
- **Deterministic Eligibility** — Rules-based logic (no LLM for high-stakes decisions)
- **RAG-Grounded Explanations** — Policy explanations cite source documents
- **Transaction Verification** — Double-check eligibility at write-time

## Setup

### Prerequisites
- Python 3.8+
- Jupyter

### Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/smart-library-assistant.git
   cd smart-library-assistant
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional for demo):
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys if integrating real services
   ```

## Running the Project

### Option 1: Interactive Notebook (Recommended)
```bash
jupyter notebook smart-library-demo.ipynb
```

**Notebook Structure (9 Cells):**
- **Cell 1**: System Setup — Imports, database initialization, assistant instantiation
- **Cell 2**: Interactive Workflow — Loan dropdown selector + "Process Renewal" button with callback
- **Cell 3**: Workflow Execution & Testing — Manual execution example with specific loan
- **Cell 4**: Golden Evaluation Scenarios — 4 test cases covering all decision branches (100% pass rate)
- **Cell 5**: Synthetic Data Generation — 210 test loans with controlled category distribution
- **Cell 6**: LangTrace Telemetry — Mock trace generation with queryable metadata
- **Cell 7**: Future Enhancements — Roadmap for v2 (persistent storage, escalation workflow)
- **Cell 8**: System Summary — Architecture overview and key design decisions
- **Cell 9**: Freeform Renewal Requests — Natural language query matching example

### Option 2: Run Python Prototype
```bash
python smart-library-renewal-prototype.py
```

Outputs evaluation metrics across all scenarios.

## Project Structure

```
smart-library-assistant/
├── smart-library-demo.ipynb          # Interactive demo (9 cells)
├── smart-library-renewal-prototype.py # Core system (~650 lines)
├── requirements.txt                   # Dependencies
├── .env.example                       # Environment template
├── .gitignore                         # Git exclude patterns
└── README.md                          # This file
```

## Key Components

### Pydantic Schemas
- `BookLoan` — Checkout record
- `Patron` — Library card holder
- `RenewalEligibilityReport` — Deterministic system verdict
- `RAGExplanationResult` — Policy retrieval metadata
- `EvalScenarioResult` — Test results

### Core Classes
- `LibraryDatabase` — Mock system of record
- `SmartLibraryAssistant` — Orchestrator
- `PolicyRetriever` — RAG engine
- `SimulatedLLMGenerator` — Natural language explanations
- `SmartLibraryEvaluator` — Evaluation framework

## Evaluation Results

**4 Golden Scenarios (100% Pass Rate):**

| Scenario | Layer Coverage | Status |
|----------|---|---|
| **EVAL-001** | Happy Path — Eligible book, user confirms, renewal completes | ✅ Pass |
| **EVAL-002** | Policy Path — Active hold blocks renewal, RAG explains policy | ✅ Pass |
| **EVAL-003** | Collection Path — New Release category blocks renewal | ✅ Pass |
| **EVAL-004** | Safety Path — Eligible book, user rejects, no write occurs | ✅ Pass |

**Aggregated Metrics:**
- Detection Layer: 100% (all due-soon loans identified)
- Decision Layer: 100% (eligibility checks accurate)
- Language Layer: 100% (RAG explanations grounded & cited)
- Tool-Call Layer: 100% (correct action routing)
- Transaction Layer: 100% (database writes verified)
- End-to-End Success: 100% (all scenarios pass)

## Submission

**Gen Academy Capstone — Sept 12, 2026**

This project demonstrates a production-grade hybrid AI system combining:
- Deterministic business logic (eligibility rules)
- LLM-assisted explanations (policy RAG)
- Human confirmation gates (HITL safety)

## Contact

For questions, see the project documentation or contact the team.
