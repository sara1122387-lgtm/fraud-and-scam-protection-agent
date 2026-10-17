# Decision Log — Fraud and Scam Protection Agent

Last updated: 2026-10-17
Project status: Initial application and development environment setup

## 1. Project Purpose

Build a small, explainable prototype that helps Iraqi digital-wallet users recognize possible scam and social-engineering signals before deciding whether to proceed with a simulated transfer.

**Core principle:**

RULES DETECT. AI EXPLAINS. THE USER DECIDES.

This is an educational prototype, not a production fraud-detection service and not an official ZainCash product or integration.

## 2. Source of Scope

The initial design brief defines the proposed user problem, workflow, candidate risk signals, evaluation approach, and scope limits.

The design brief is a starting point. Material changes to scope, architecture, privacy safeguards, or evaluation should be recorded in this file.

## 3. Confirmed MVP Decisions

### D-001: Technology

**Decision:** Use Python and Streamlit for the initial prototype.

**Status:** Chosen. The local environment and initial Streamlit interface have been set up. The complete application workflow still needs to be implemented and tested.

### D-002: Rules-first assessment

**Decision:** Use explicit, understandable rules as the foundation of risk assessment. An LLM must not be the sole authority for a risk decision.

**Status:** Chosen. Detection rules have not yet been implemented.

### D-003: AI coaching

**Decision:** If an LLM is added, its role will be to explain identified signals in clear Iraqi Arabic, based on available evidence. It must not invent transaction facts or present uncertainty as certainty.

**Status:** Chosen in principle. The provider, integration, and safeguards remain undecided.

### D-004: Simulated user choice

**Decision:** The prototype may let a user choose to cancel or simulate proceeding within a simulated flow. It must not initiate a real wallet transfer.

**Status:** Chosen. The decision flow has not yet been implemented.

### D-005: Synthetic data only

**Decision:** Use synthetic scenarios for development and evaluation. Do not use real customer records or connect to a live wallet.

Never request or store wallet passwords, OTPs, private keys, or payment credentials.

**Status:** Chosen. Implementation safeguards and tests remain to be added.

### D-006: Minimum necessary input

**Decision:** Prefer a small set of structured context fields, with an optional pasted message only if it is useful to the assessment. Collect only information necessary for the intended workflow.

Exact fields, validation rules, and handling of optional message text remain to be finalized.

### D-007: Evaluation

**Decision:** Include scam, legitimate, ambiguous, and incomplete scenarios. Keep the held-out evaluation set separate from scenarios used to develop or tune rules and prompts.

Planned measures include precision, recall, false-positive rate, and failure analysis. Metrics must be reported with their dataset, evaluation conditions, and limitations.

**Status:** Planned. The dataset, evaluation procedure, and results are not yet available.

### D-008: Evidence and uncertainty

**Decision:** Distinguish observed inputs from inferred risk signals. Explain the reasons for an assessment and communicate uncertainty. A risk signal is not proof of fraud.

**Status:** Chosen. The assessment and explanation logic has not yet been implemented.

### D-009: Scope control

**Keep in the initial MVP:**

- Explainable, rule-based risk assessment
- Clear reasons supporting warnings
- Optional Iraqi-Arabic coaching, if safely integrated
- A simulated cancel/proceed choice
- Minimal, privacy-conscious evaluation logging
- Labeled synthetic scenario evaluation

**Defer:**

- Live wallet integration
- Voice or call analysis
- Continuous monitoring
- Advanced behavioral profiling
- Training mode and other nonessential features
- Custom model training and unnecessary infrastructure

Reconsider deferred features only after the core prototype works and has been evaluated.

## 4. Decisions Still Open

- LLM provider and whether an external LLM is necessary
- Risk-scoring method and rule weights
- Final input fields and validation rules
- Size, composition, and labeling procedure for the synthetic dataset
- Safe handling or redaction of optional pasted text before any external API call
- Which evaluation metadata must be recorded
- Deployment approach

Open decisions must not be described as implemented features. Any selected external service must be documented along with its role and relevant data-handling implications.

## 5. Intended End-to-End Flow

1. Collect the minimum necessary context.
2. Validate inputs.
3. Apply explicit rules to the available evidence.
4. Produce an assessment with reasons and uncertainty.
5. Optionally generate Iraqi-Arabic coaching grounded in the assessment.
6. Present verification advice and a simulated user choice.
7. Record only necessary, non-sensitive evaluation information, if logging is needed.
8. Evaluate results against labeled synthetic scenarios.

This is the intended design, not a claim that these stages already work.

## 6. Privacy and Safety Constraints

- Use synthetic data only.
- Never ask users to submit passwords, OTPs, wallet credentials, private keys, or payment credentials.
- Do not perform real transfers or claim official wallet integration.
- Do not commit API keys, secrets, or local environment files.
- Do not send pasted messages to an external service until data handling, disclosure, and safeguards have been designed and tested.
- Do not claim that text redaction is perfect.
- Avoid collecting or logging unnecessary personal or financial information.
- If logging is implemented, restrict it to information necessary for testing and evaluation; exclude credentials, secrets, and sensitive message content.
- Treat risk indicators as evidence to examine, not proof of wrongdoing.
- Preserve the user's ability to make an informed decision.
- Disclose external models, tools, datasets, and AI coding assistants used in development.

## 7. Milestones

1. **Foundation:** Establish the repository, development environment, initial interface, and documentation.
2. **Test design:** Define synthetic scenarios, expected labels, and a separate held-out evaluation set.
3. **Detection core:** Implement explainable rules, input validation, and unit tests.
4. **End-to-end workflow:** Connect the interface to the detection logic, explanations, and simulated user choice.
5. **Evaluation:** Measure false positives, missed cases, and performance on ambiguous or incomplete inputs.
6. **Optional AI coaching:** Consider LLM integration only after the rules-first core is stable and tested.
7. **MVP preparation:** Document actual results, observed failure cases, limitations, and reproducible setup steps.

Milestone completion must reflect verified implementation, not merely planned work.

## 8. Change Log

### 2026-10-17 — Initial foundation

- Created the GitHub repository and local clone.
- Set up a Python virtual environment.
- Installed Streamlit and Pytest.
- Added dependency declarations and began project documentation.
- Established the initial Streamlit interface.
- No detection rules, complete simulated decision flow, synthetic evaluation suite, or AI coaching have been implemented and verified at this stage.
