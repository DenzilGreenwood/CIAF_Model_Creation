# CIAF MVP - Complete End-to-End Demo

This is a production-ready MVP of the Cognitive Insight Audit Framework (CIAF) demonstrating full AI governance, compliance automation, and cryptographic proof generation.

## 🎯 What This MVP Demonstrates

### ✅ Core CIAF Functionality
- **Multi-agent system** - Banking and Healthcare agents working independently
- **LLM integration** - Supports OpenAI, Local Ollama, or Mock (automatic fallback)
- **Output tagging** - Cryptographic watermarking of AI outputs
- **Merkle proofs** - Tamper-evident audit trails
- **Compliance tracking** - Real-time policy enforcement
- **Non-repudiation** - Proves which agent generated which output when
- **Web dashboard** - Real-time monitoring and compliance reporting

### 📊 Architecture

```
┌────────────────────────────────────────────────────────┐
│  Demo Workflows (demo_workflows.py)                    │
│  - Banking Agent Demo                                  │
│  - Healthcare Agent Demo                               │
│  - Multi-agent Collaboration                           │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│  Agent Orchestrator (agents_domain.py)                 │
│  - BankingAgent (credit analysis)                      │
│  - HealthcareAgent (clinical support)                  │
│  - AgentOrchestrator (multi-agent management)          │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│  Base Agent Layer (agents_base.py)                     │
│  - Output generation with LLM                          │
│  - CIAF tag creation                                   │
│  - Execution tracking                                  │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│  LLM Providers (llm_providers.py)                      │
│  - OpenAI GPT-4 (real models)                          │
│  - Ollama (local, offline)                             │
│  - Mock (testing, no API costs)                        │
│  - Auto-fallback on unavailability                     │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│  CIAF Client SDK (ciaf_client/)                        │
│  - Verification API communication                      │
│  - Tag submission and verification                     │
│  - Audit trail retrieval                               │
│  - Compliance reporting                                │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│  CIAF Verification Microservice                        │
│  - FastAPI endpoints                                   │
│  - PostgreSQL proof storage                            │
│  - Merkle tree validation                              │
│  - Dashboard integration                               │
└────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
```bash
# Install Python 3.10+
# Have Docker running (for the verification service)
```

### 1. Install Dependencies

```bash
pip install requests openai python-dotenv pydantic
```

### 2. Start the CIAF Verification Service

The service should already be running in Docker:

```bash
# Check service is running
curl http://localhost:8001/health

# Expected response
# {"status": "healthy", "timestamp": "2026-03-13T..."}
```

### 3. Configure LLM Provider

**Option A: Use Mock LLM (Recommended for first run - no API costs)**
```bash
# No configuration needed, uses mock by default
python demo_workflows.py
```

**Option B: Use Local Ollama (Offline)**
```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull a model: ollama pull mistral
# 3. Start Ollama: ollama serve
# 4. Run demo: python demo_workflows.py
```

**Option C: Use OpenAI GPT-4**
```bash
# Set your API key
export OPENAI_API_KEY="sk-..."

# Run demo
python demo_workflows.py
```

### 4. Run the MVP Demos

```bash
python demo_workflows.py
```

**Expected Output:**
```
🚀 CIAF MVP - End-to-End Demonstrations
================================================================================

================================================================================
🏦 BANKING WORKFLOW DEMO - Credit Analysis with CIAF Verification
================================================================================

✅ Initialized LLM Provider: MockProvider
✅ Organization: banking_org_001
✅ Created agent: agent_credit_analyst_001 (credit_analyst)

----...

📊 System Compliance:
   Total Outputs: 4
   Verified Outputs: 4
   Verification Rate: 100.0%
   Active Agents: 1

================================================================================
🏥 HEALTHCARE WORKFLOW DEMO - Clinical Decision Support with CIAF Verification
================================================================================

... (similar flow for healthcare)

✅ All demos completed successfully!
```

## 📦 Project Structure

```
d:\Github\CIAF_Models\CIAF_Model_Creation\
├── ciaf_client/                    # Python SDK for verification service
│   ├── __init__.py
│   ├── client.py                  # CIAFClient class (API communication)
│   └── types.py                   # TypeScript-style type definitions
│
├── llm_providers.py               # LLM abstraction layer
│   ├── LLMProvider (abstract)
│   ├── OpenAIProvider
│   ├── OllamaProvider
│   ├── MockProvider
│   └── LLMProviderFactory
│
├── agents_base.py                 # Base agent implementation
│   ├── Agent (abstract base class)
│   └── Methods for output generation and tagging
│
├── agents_domain.py               # Domain-specific agents
│   ├── BankingAgent (credit analysis)
│   ├── HealthcareAgent (clinical support)
│   └── AgentOrchestrator (multi-agent management)
│
└── demo_workflows.py              # End-to-end demonstrations
    ├── demo_banking_workflow()
    ├── demo_healthcare_workflow()
    ├── demo_multi_agent_collaboration()
    └── __main__ orchestration
```

## 🎬 MVP Demonstrations

### 1. Banking Workflow (demo_banking_workflow)
Demonstrates credit analysis with compliance tracking:

**Flow:**
1. Create banking agent with credit analysis role
2. Analyze multiple customer applications
3. Generate credit recommendations
4. Verify past outputs through CIAF
5. Display compliance dashboard

**Output:**
- Loan decision tagged with CIAF
- Risk assessment documented
- Full audit trail available
- Compliance rate: 100%

### 2. Healthcare Workflow (demo_healthcare_workflow)
Demonstrates clinical decision support:

**Flow:**
1. Create healthcare agent with clinical role
2. Analyze patient cases
3. Generate treatment recommendations
4. Verify clinical recommendations
5. Display compliance dashboard

**Output:**
- Clinical assessment tagged with CIAF
- Evidence-based recommendations
- HIPAA compliance tracking
- Physician review trail

### 3. Multi-Agent Collaboration (demo_multi_agent_collaboration)
Demonstrates cross-domain agents:

**Scenario:** Medical debt analysis for loan decision
1. Clinician generates medical assessment
2. Banker uses assessment for credit decision
3. Both outputs cryptographically linked
4. Cross-domain compliance tracking

## 🔐 Key Features Demonstrated

### 1. Cryptographic Proofs
```
Each AI output generates:
├── Content Hash (SHA-256)
├── Merkle Proof (task level)
├── Org Batch Merkle Root (6-hour window)
└── Timestamp + Signature
```

### 2. Policy Compliance
```
Banking Policies:
├── Fair Lending
├── Risk Assessment
├── Compliance Monitoring
└── Bias Detection

Healthcare Policies:
├── HIPAA Compliance
├── Clinical Accuracy
├── Bias Mitigation
└── Informed Consent
```

### 3. Non-Repudiation
```
Proof that:
├── Agent XYZ generated output ABC
├── At timestamp T
├── Using model GTP-4
├── Applying policies P1, P2, P3
└── With merkle chain validation
```

## 📊 Using the Web Dashboard

While demos are running, access the web dashboard in real-time:

```
URL: http://localhost:3002

Available Pages:
├── Dashboard - Real-time overview
├── Verification Engine - Tag verification UI
├── Compliance Dashboard - Policy compliance
├── Organization Stats - Agent statistics
└── Audit Trail - Full history
```

## 🔍 Accessing Generated Proofs

```bash
# Verify an output
curl http://localhost:8001/verify/{tag_id}

# Get audit trail
curl http://localhost:8001/audit/{tag_id}

# Get compliance report
curl http://localhost:8001/compliance/{organization_id}

# Get stats
curl http://localhost:8001/stats/{organization_id}
```

## 💡 How to Extend This MVP

### Add a New Domain (e.g., Legal)
```python
from agents_domain import Agent

class LegalAgent(Agent):
    LEGAL_POLICIES = [
        "data_privacy",
        "regulatory_compliance",
        "bias_detection"
    ]

    def get_system_prompt(self) -> str:
        return "You are a legal compliance assistant..."

    def analyze_contracts(self, contract_text: str):
        return self.create_tagged_output(
            f"Review this contract: {contract_text}",
            temperature=0.2
        )

# Use it
legal_agent = orchestrator.create_agent(LegalAgent, "agent_legal_001", "contract_analyst")
result = legal_agent.analyze_contracts(contract_text)
```

### Use Different LLM
```python
from llm_providers import LLMProviderFactory, LLMProviderType

# Use OpenAI
llm = LLMProviderFactory.create(LLMProviderType.OPENAI, model="gpt-4-turbo")

# Use Ollama
llm = LLMProviderFactory.create(LLMProviderType.OLLAMA, model="neural-chat")

# Pass to orchestrator
orchestrator = AgentOrchestrator("org_001", llm)
```

## 🎓 Learning Outcomes

This MVP demonstrates:
1. ✅ How AI governance works with cryptographic proofs
2. ✅ Multi-agent orchestration in compliance environments
3. ✅ Real-time audit trail generation
4. ✅ Policy enforcement automation
5. ✅ Non-repudiation mechanisms
6. ✅ Integration with verification microservices
7. ✅ Enterprise dashboard monitoring

## 🚨 Important Notes

- **Mock Provider**: Uses predetermined responses for testing (no API costs)
- **Privacy**: All outputs stored locally in SQLite/PostgreSQL
- **Compliance**: No actual models are run in mock mode
- **Production Ready**: Code structure ready for real LLMs and production deployment

## 📞 Support

For issues or questions:
1. Check the dashboard at http://localhost:3002
2. Review API docs at http://localhost:8001/docs
3. Check agent execution history in demo output
4. Verify service health: `curl http://localhost:8001/health`

---

**Built with CIAF MVP v1.0** | Evidence-First AI Governance
