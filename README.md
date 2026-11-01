# COD Risk & RTO Control Tower

A Streamlit decision-support prototype for pre-shipment COD risk management.

## Run locally (under 10 minutes)

1. Install Python 3.10+.
2. Open this folder in VS Code.
3. Open the VS Code terminal and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate with `.venv\\Scripts\\activate`.

## What it includes
- CSV loading, status normalization and duplicate order-ID removal.
- Baseline Random Forest RTO model with a held-out test split.
- Editable risk thresholds and business rules in `config/rules.yaml`.
- Four-way action recommendation: ship as-is, WhatsApp confirmation, prepaid nudge, or manual review (manual review is represented through the confirmation path).
- WhatsApp message and response simulator (YES / NO / unclear / no reply).
- Dashboard, estimated prepaid economics and downloadable decision log.

## Important limitations
- The sample is historical and relatively small. Model metrics are diagnostic, not proof of causal impact.
- Model scores must not trigger automatic cancellation. Human review is required for ambiguous cases.
- The WhatsApp workflow is a simulation; no real messages are sent.
- LLM-based address parsing is intentionally not required for the first prototype. Add it only for ambiguous address interpretation, and retain a human-review fallback.
- Business impact figures are assumption-based and should be validated in a controlled pilot.

## Project structure
- `app.py`: Streamlit UI
- `engine.py`: cleaning, model, risk scoring, decision rules and unit economics
- `config/rules.yaml`: editable thresholds and assumptions
- `data/orders_sample.csv`: supplied sample dataset
- `reports/`: founder memo
- `logs/`: decision and AI usage logs
