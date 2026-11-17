# Climate Implementation Readiness Lab V1.0

**COP31 AI Solutions Lab | Day 11 — November 19, 2026**

An educational Python/Streamlit application for exploring how documentation gaps affect the preparation of proposed climate projects. It uses **three entirely synthetic projects** and a transparent, equal-weight checklist. **This is not an investment-readiness certification, funding assessment, or operational decision tool.**

## Four modules

1. **Project Portfolio Overview:** synthetic water, energy, and urban-resilience projects; summary charts.
2. **Implementation Readiness Assessment:** ten documented/partial/missing criteria, gap explanations, and reproducible documentation scores.
3. **AI & Human Review:** optional Gemini 2.5 Flash structured narrative and human-review records in local SQLite.
4. **Export & Methodology:** indicators and review CSV, complete JSON, SHA-256 fingerprint, and limitations.

## Setup (Windows / PyCharm)

Python 3.11–3.12 recommended; no GPU required.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

For optional Gemini, copy `.env.example` to `.env` and insert your key. Never publish `.env`. The app works without AI access.

## Synthetic project examples

- **Municipal Water Loss Reduction** — leak detection and network efficiency.
- **Public Building Energy Retrofit** — building energy-use reduction proposal.
- **Urban Flood Resilience Upgrade** — drainage and green-infrastructure planning.

## Transparent methodology

Ten equally weighted fields: problem definition, evidence, stakeholders, governance, budget, funding, timeline, indicators, risks, and maintenance. `documented = 1`, `partial = 0.5`, `missing = 0`; score = `100 × sum / 10`. Scores indicate **checklist documentation completeness only**, not scientific evidence quality, feasibility, cost-effectiveness, funding eligibility, or expected climate impact.

Every record is fabricated for education. No real financial estimates, beneficiaries, permits, impact measurements, COP31 negotiation outcomes, or claims of achieved results are included. A human must validate any AI narrative. SHA-256 can identify changes in a dataset but does not provide immutable provenance.

## Tests

Run `python -m pytest -q` to test calculations, data validation, audit records, and the optional API-key guard. The test suite does not perform a live Gemini request or validate Streamlit visually.

**Evidence first. Engineering second. Measurable impact as the goal.**
