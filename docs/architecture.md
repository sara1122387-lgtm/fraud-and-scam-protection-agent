# System Architecture — Fraud and Scam Protection Agent

## 1. Project Status

**Current status:** Initial repository, development environment, and Streamlit interface established.

The current application provides an initial interface only. Risk-assessment rules, synthetic evaluation data, automated tests for detection, simulated decision handling, and AI coaching have not yet been implemented and verified.

This document describes the intended architecture and development plan. Planned components must not be presented as completed functionality.

## 2. Target User and Problem

The prototype targets Iraqi digital-wallet users who may encounter scams or social-engineering attempts while preparing a transfer.

Users may be pressured to act quickly, disclose sensitive information, pay fictitious fees, or redirect money to an untrusted recipient. The prototype aims to help users examine relevant warning signs before making a decision.

**Project principle:**

RULES DETECT. AI EXPLAINS. THE USER DECIDES.

The project is an independent prototype. It is not an official ZainCash product or integration and does not execute real wallet transfers.

## 3. End-to-End Architecture

The planned workflow is:

1. **Input Context:** Collect a small set of relevant fields describing a simulated transfer and, if appropriate, a synthetic suspicious message.
2. **Input Validation:** Check required fields, accepted values, and incomplete inputs. Avoid collecting unnecessary personal or financial information.
3. **Rule-Based Detection:** Apply explicit, understandable rules to the available evidence and identify potential risk signals.
4. **Risk Assessment:** Combine applicable signals into a transparent assessment. Keep observed facts distinct from inferred risk and communicate uncertainty.
5. **Explanation and Coaching:** Generate a clear explanation grounded in the identified evidence. Optional LLM-assisted coaching may provide Iraqi-Arabic guidance, but the LLM must not be the sole authority for the risk decision.
6. **Simulated User Decision:** Allow the user to choose Cancel or Simulate Proceed within the prototype. Neither choice initiates a real transfer.
7. **Evaluation:** Compare system outputs with labels in a synthetic evaluation set, measure performance, and investigate false positives, missed cases, and other failure modes.

These stages describe the intended workflow. They are not all implemented yet.

## 4. Planned Components

- `app.py` — Streamlit interface for the prototype.
- `src/` — Planned input validation, rule-based detection, risk assessment, and supporting application logic.
- `data/` — Planned synthetic scenarios and labeled evaluation data.
- `tests/` — Planned automated tests for input validation, detection rules, and assessment behavior.
- `docs/` — Project architecture, decisions, and development documentation.
- `requirements.txt` — Direct Python dependency declarations.
- `requirements-lock.txt` — Intended pinned dependency set for reproducible setup, subject to compatibility verification.

The `src/`, `data/`, and `tests/` directories are planned and should not be considered implemented until their contents exist and have been tested.

## 5. Models, Tools, and Data

### Core Technology

- **Python:** Application logic and risk-assessment rules.
- **Streamlit:** User interface for the prototype.
- **Pytest:** Automated testing.
- **Git and GitHub:** Version control, project history, and documentation.

### Detection and AI

The core risk assessment will use explicit rules with understandable supporting evidence. Simple statistics may be used where appropriate for combining signals or evaluating results.

An external large language model (LLM) is optional. If integrated, its role will be to explain already identified signals and provide Iraqi-Arabic coaching grounded in supplied evidence. The provider and integration approach remain undecided until the rules-first core is stable and testable.

A deterministic explanation path should remain available if an external AI service is unavailable or produces an unusable response.

### Data Policy

Development and evaluation will use synthetic data only. No real customer records, live transaction data, wallet credentials, passwords, one-time passwords (OTPs), or private keys will be collected or used.

Any external AI integration must be evaluated for privacy, data handling, disclosure, and failure behavior before use.

## 6. Synthetic Evaluation Plan

The evaluation set will contain labeled synthetic **scenarios**, not a claimed number of real or representative users.

Scenarios should cover:

- **Potential scams:** Impersonation, requests for OTPs, fictitious fees, suspicious redirection, urgency, and combinations of risk signals.
- **Legitimate activity:** Ordinary transfers, legitimate new recipients, and unusual but genuine transactions.
- **Ambiguous or incomplete cases:** Inputs that do not provide enough evidence for a confident assessment.

Scenarios used to develop or tune rules must be kept separate from the held-out test set. The held-out cases must not be used to tune rules or prompts.

Planned evaluation measures include:

- **Precision:** The proportion of flagged scenarios that are labeled as scams in the evaluation set.
- **Recall:** The proportion of labeled scam scenarios that the system identifies.
- **False-positive rate:** The proportion of labeled legitimate scenarios incorrectly flagged.
- **Failure analysis:** Documented review of missed scams, false alarms, ambiguous cases, and other important failure modes.

The final dataset size, label distribution, and acceptance criteria remain to be finalized. Results must be reported with the test-set size and limitations; a small synthetic evaluation does not establish real-world effectiveness.

## 7. Risks and Mitigations

- **False positives:** Provide reasons for warnings and measure how often legitimate scenarios are flagged.
- **False negatives:** Review missed scam scenarios and document the limitations of the rules.
- **Ambiguous or incomplete inputs:** Communicate uncertainty and recommend independent verification rather than making unsupported claims.
- **LLM hallucinations:** Ground explanations in the evidence produced by the detection stage, and retain a deterministic fallback.
- **Privacy exposure:** Use synthetic inputs, minimize data collection, protect credentials, and assess external-service data handling before integration.
- **Overconfidence:** Present assessments as decision support, not proof that a transaction is fraudulent or safe.
- **Service or network failure:** Keep the core assessment independent of optional external AI availability.
- **Scope and schedule risk:** Prioritize a working, testable rules-first workflow over optional integrations and advanced features.

## 8. Development Plan and Milestones

### Before 22 October 2026 — Design Brief

- Align the repository documentation with the agreed project scope.
- Finalize the end-to-end architecture, tools, risks, evaluation approach, and MVP milestones.
- Publish the GitHub repository link and maintain accurate implementation status.

### 23–29 October — Core Foundation

- Define input fields, validation behavior, risk signals, and the initial rule structure.
- Create an initial synthetic scenario set with documented expected labels.
- Implement the first version of the rules and focused automated tests.

### 30 October–1 November — End-to-End Workflow

- Connect the assessment logic to the Streamlit interface.
- Display risk levels, supporting evidence, and uncertainty.
- Implement the simulated Cancel and Simulate Proceed choices.
- Check that no action initiates a real transfer.

### 2–4 November — Evaluation and Reliability

- Separate development scenarios from held-out test scenarios.
- Run the tests and evaluate the system on the held-out set.
- Review false positives, missed cases, ambiguous inputs, and other observed failures.
- Fix important defects and record measured results without inventing performance claims.

### 5–7 November — Stabilization and Documentation

- Verify setup instructions and dependency compatibility.
- Test the complete workflow from input to assessment and simulated decision.
- Document known limitations and at least three observed failure modes with their handling.
- Prepare the one-page MVP update and a reliable demonstration path.

### By 8 November 2026 — MVP Submission

Deliver a working core workflow on sample inputs, a GitHub repository with meaningful commit history, initial results on the held-out synthetic test set, and a one-page update describing what works, what does not, and what comes next.

Optional LLM coaching may be added only if the core workflow, testing, and documentation are stable. It is not a prerequisite for a reliable rules-first MVP.

These milestones are a proposed execution plan, not a claim that the work has already been completed.

## 9. Scope Boundaries

### Included in the MVP

- Explainable, rules-first risk assessment.
- Clear reasons supporting warnings.
- Synthetic labeled scenarios and automated tests.
- Evaluation of false positives, missed cases, and other failure modes.
- Simulated Cancel or Proceed choices.
- Optional Iraqi-Arabic LLM coaching only if time, privacy safeguards, and reliability permit.

### Out of Scope

- Live ZainCash integration or real wallet transfers.
- Automatic blocking of real payments.
- Real customer or transaction data.
- Voice or call analysis.
- Continuous transaction monitoring.
- Advanced behavioral profiling.
- Custom model training or unnecessary agent frameworks and retrieval infrastructure.

The user retains control over the final simulated decision. A risk signal is evidence to examine, not proof of fraud, and the prototype must not claim production-level protection.