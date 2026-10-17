# Fraud and Scam Protection Agent

**A deliberate pause before a risky wallet transfer**

> RULES DETECT. AI EXPLAINS. THE USER DECIDES.

## Overview

Fraud and Scam Protection Agent is an independent prototype intended to help Iraqi digital-wallet users recognize potential scam and social-engineering signals before deciding whether to proceed with a transfer.

The planned system combines explainable, rule-based risk assessment with clear explanations and optional Iraqi-Arabic AI coaching. Its purpose is to help users examine warning signs and make more informed decisions, not to make decisions on their behalf.

This project is independent. It is not an official ZainCash product and does not integrate with ZainCash or any live wallet service.

## Current Status

**Stage: Initial application and development environment setup.**

The Git repository, Python virtual environment, project dependencies, and initial Streamlit interface have been established. The interface runs locally.

The following components are planned but have not yet been implemented and verified:

- Rule-based risk assessment
- Synthetic scenario dataset and automated evaluation
- Iraqi-Arabic AI coaching
- Simulated transfer decision flow
- Evaluation metrics and failure analysis

**The current application is not a working fraud detector.** Planned functionality must not be presented as implemented or tested until it has been verified.

## Planned Workflow

1. **Context:** Collect minimal, relevant transaction context in a simulated environment.
2. **Validation:** Check inputs for missing or invalid information.
3. **Detection:** Apply explicit rules to identify potential risk signals.
4. **Assessment:** Produce a transparent risk assessment supported by relevant evidence, with uncertainty made visible.
5. **Coaching:** Optionally provide Iraqi-Arabic explanations grounded in the available evidence.
6. **User decision:** Allow the user to choose `Cancel` or `Proceed` within the simulation.
7. **Evaluation:** Compare assessments against labeled synthetic scenarios and review failure cases.

This workflow describes the intended design, not completed functionality.

## Scope

### Planned for the Initial Prototype

- Explainable, rules-first risk assessment
- Clear reasons supporting warnings
- Optional Iraqi-Arabic AI coaching
- Simulated user decisions
- Labeled synthetic test scenarios
- Evaluation of false positives, missed cases, and other failure patterns
- Minimal logging for testing and evaluation

### Out of Scope

- Real wallet transfers
- Live ZainCash integration
- Real customer or transaction data
- Voice or call analysis
- Continuous transaction monitoring
- Advanced behavioral profiling
- Automatic blocking of real payments
- Custom model training or unnecessary infrastructure

## Privacy and Safety

- Use synthetic data only.
- Never enter real wallet credentials, passwords, one-time passwords (OTPs), private keys, or payment credentials.
- Do not use real customers' personal or financial information.
- Never commit API keys, passwords, or other secrets to source control.
- Define data-handling and privacy safeguards before connecting an external AI service.
- If an external model is used, send only suitable synthetic inputs.
- Treat risk assessments as guidance, not proof that a transaction or recipient is fraudulent.

## Technology

- **Python:** Application logic
- **Streamlit:** Prototype interface
- **Pytest:** Automated testing
- **Git and GitHub:** Version control and project history
- **Explicit rules and simple statistics:** Planned explainable risk assessment
- **External large language model (LLM):** Optional Iraqi-Arabic coaching; provider not yet selected

## Synthetic Data and Evaluation Plan

The planned evaluation will cover labeled synthetic **scenarios**, including:

- **Potential scams:** Impersonation, requests for OTPs, fake fees, and suspicious redirection.
- **Legitimate transfers:** Genuine transfers to new recipients and unusual but legitimate transactions.
- **Ambiguous cases:** Situations where the available evidence is insufficient.
- **Incomplete or invalid inputs:** Cases that cannot be assessed reliably because required information is missing or invalid.

The final dataset size, labeling procedure, and acceptance criteria remain to be defined. No dataset size or performance result is claimed here.

Scenarios used to develop or tune the rules must be kept separate from a held-out evaluation set. The held-out set must not be used to tune the rules or prompts.

Planned evaluation measures include:

- **Precision:** The proportion of cases flagged as scams that are labeled as scams.
- **Recall:** The proportion of labeled scam cases correctly flagged by the system.
- **False-positive rate:** The proportion of legitimate cases incorrectly flagged.
- **Failure analysis:** Review of missed scams, incorrect warnings, ambiguous cases, and invalid-input handling.

Results will be reported only after the implementation, test data, and evaluation procedure are available. Any reported metrics must identify the dataset and evaluation conditions.

## Limitations

This is an experimental prototype. It cannot guarantee fraud detection, establish a recipient's identity or intent, or replace independent verification.

A warning indicates potential risk, not certainty. Missing or misleading information may prevent a reliable assessment, and legitimate transactions may trigger warnings.

Optional AI-generated explanations may be inaccurate. If AI coaching is implemented, its output must be grounded in available evidence, and a deterministic fallback should be available when the model is unavailable or produces unsuitable output.

## Local Setup

### Requirements

- Python compatible with the project's dependencies
- Git
- Visual Studio Code or another code editor

### 1. Clone the Repository

Run these commands in PowerShell:

```powershell
git clone https://github.com/sara1122387-lgtm/fraud-and-scam-protection-agent.git
cd fraud-and-scam-protection-agent
```

### 2. Create a Virtual Environment

```powershell
py -m venv .venv
```

### 3. Activate the Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, follow a documented, narrowly scoped Windows setup procedure rather than changing machine-wide security settings.

### 4. Install Dependencies

Install the supported dependency ranges:

```powershell
python -m pip install -r requirements.txt
```

The repository also contains `requirements-lock.txt`, intended to record exact dependency versions. Verify that file's consistency and compatibility before relying on it for reproducible installations.

### 5. Run the Application

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

### 6. Run Automated Tests

```powershell
python -m pytest
```

Automated tests must be added and executed as development progresses. Until test files exist and the command has been run successfully, this command does not demonstrate that the application has passed testing.

## Project Documentation

- `DECISIONS.md` — Project decisions, constraints, open questions, and milestones.
- `docs/architecture.md` — Intended system architecture, component boundaries, and workflow.
- `requirements.txt` — Supported dependency version ranges.
- `requirements-lock.txt` — File intended to record pinned dependency versions; its consistency should be verified.
- `app.py` — Streamlit application entry point.

Some planned directories and components may not yet exist.

## Development Principles

- Prefer explainable rules over unsupported or unexplained predictions.
- Separate observed evidence from interpretation.
- Make uncertainty visible.
- Evaluate both scam and legitimate scenarios.
- Keep development and held-out evaluation data separate.
- Use synthetic data and protect sensitive information.
- Document limitations, failure cases, and measured results honestly.
- Disclose external models, tools, datasets, and AI coding assistants used in development.
- Keep the prototype small, testable, and within scope.
