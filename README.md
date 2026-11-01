# COD Risk & RTO Control Tower

A Streamlit-based decision-support prototype for pre-shipment Cash on Delivery (COD) risk management. It analyzes historical order data, estimates RTO risk, and recommends operational actions to reduce avoidable returns.

## Run locally (under 10 minutes)

**Requirements:** Python 3.10+

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start dashboard
streamlit run app.py
```

On Windows, activate the environment using:

```bash
.venv\Scripts\activate
```

## Features

- CSV loading, data cleaning, status normalization and duplicate order-ID removal.
- Random Forest baseline model with a held-out test split.
- Configurable risk thresholds and business assumptions in `config/rules.yaml`.
- Four-way order decision policy:
  1. `SHIP_AS_IS` – low-risk orders.
  2. `WHATSAPP_CONFIRM` – orders requiring customer confirmation.
  3. `PREPAID_NUDGE` – eligible orders offered a prepaid incentive.
  4. `HOLD_REVIEW` – orders requiring manual review due to severe data-quality concerns.
- WhatsApp message and response simulator (YES / NO / unclear / no response).
- Dashboard with decision counts, estimated RTO economics and downloadable decision records.

## Model and business assumptions

The model uses historical order attributes to estimate RTO risk. Its output supports decision-making; it is not a standalone cancellation mechanism.

The financial scenario uses the assignment assumptions:
- COD RTO rate: 28%
- Prepaid RTO rate: 4%
- Expected cost per RTO: ₹169.40
- Prepaid discount scenario: ₹20
- Estimated net benefit per successful COD-to-prepaid conversion: ₹20.66

These are estimates, not measured savings or guaranteed outcomes.

## Limitations and safeguards

- The dataset is historical and relatively small. Model metrics are diagnostic, not proof of causal impact.
- Model scores must not trigger automatic cancellation. Ambiguous cases require human review.
- The WhatsApp workflow is simulated; no real messages are sent.
- The current prototype uses deterministic data-quality checks. It does not yet implement an LLM-powered Hinglish or nuanced address interpretation workflow.
- Business impact figures are assumption-based and should be validated through a controlled pilot.
- Monitor false positives, genuine-order cancellations and customer complaints before scaling.

## Project structure

```text
cod-risk-rto-engine/
├── app.py
├── engine.py
├── config/
│   └── rules.yaml
├── data/
│   └── orders_sample.csv
├── reports/
│   ├── founder_memo.md
│   ├── founder_memo.pdf
│   └── data_quality_summary.json
├── logs/
│   ├── decision_log.md
│   └── ai_usage_log.md
├── requirements.txt
└── README.md
```

## Submission artifacts

- `reports/founder_memo.pdf` – founder-facing business memo.
- `reports/founder_memo.md` – editable memo source.
- `logs/decision_log.md` – decision-policy documentation.
- `logs/ai_usage_log.md` – AI assistance and validation record.

## Future improvements

- Optional LLM-based address interpretation for ambiguous and Hinglish addresses, with structured output and human-review fallback.
- Integration with a real WhatsApp Business API.
- Randomized pilot evaluation to measure actual incremental savings.
- Model monitoring and threshold calibration as more delivery outcomes become available.

## LLM-Assisted Address Validation

The project integrates a locally hosted Qwen 2.5 (3B) model through Ollama
to identify ambiguous or incomplete customer addresses.

### How it works
- Sends address, city, state, and PIN code to the local LLM.
- Requests structured JSON containing ambiguity status, missing information,
  normalized address, and recommendation.
- Applies deterministic safeguards for vague landmarks, missing addresses,
  short addresses, and invalid PIN codes.
- Flags ambiguous orders for manual confirmation before dispatch.

### Setup
1. Install Ollama: https://ollama.com/
2. Pull the model:

   `ollama pull qwen2.5:3b`

3. Start the Ollama service.
4. Install project dependencies:

   `pip install -r requirements.txt`

5. Launch the dashboard:

   `streamlit run app.py`

### Limitations
- Runs locally; no external LLM API key is required.
- Model responses may be inaccurate or incomplete.
- Deterministic checks act as safeguards but cannot guarantee address validity.
- Ambiguous addresses require human review. The LLM does not automatically
  cancel orders.