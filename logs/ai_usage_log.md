# AI Usage Log

## Tools used
- ChatGPT: assistance with project architecture, Python implementation, debugging, decision-policy design and business memo drafting.
- VS Code: local development and execution.
- Streamlit: dashboard and WhatsApp workflow simulation.
- Git and GitHub: version control and project submission.

## AI assistance and validation

| Task | AI-assisted output | Validation performed |
|---|---|---|
| Project architecture | Suggested a modular Python and Streamlit application | Ran the application locally and checked the dashboard |
| Data processing | Suggested duplicate removal and status normalization | Checked unique order IDs, missing fields and normalized outcomes |
| Risk policy | Suggested risk-based order routing | Tested the dashboard and identified that the fourth action was not initially being assigned |
| Business memo | Suggested financial calculations and findings | Rechecked the order counts and assignment unit economics |

## Examples of weak AI output identified and corrected

**1. The fourth decision bucket was not fully implemented.**

- Initial issue: The first implementation did not assign orders to a distinct hold/manual-review action.
- How it was identified: The dashboard showed zero hold/review orders.
- Correction: Added a separate `HOLD_REVIEW` decision for severe data-quality concerns and verified that all four buckets appeared in the dashboard.

**2. A historical order count in an early memo draft was incorrect.**

- Initial issue: The draft stated 1,444 delivered orders.
- How it was identified: This did not reconcile with 1,987 labeled orders and 565 RTO orders.
- Correction: The correct delivered count is 1,422, after excluding the in-transit record.

**3. The model's predictive performance could be overstated.**

- Initial issue: Accuracy alone could make the model appear sufficient for automated cancellation.
- How it was identified: Held-out RTO recall was only 48.94%.
- Correction: The policy uses the model for routing and confirmation, not automatic cancellation. Unclear cases remain subject to human review.

## Limitations

The project uses a historical sample and a simulated WhatsApp workflow. It does not send real messages or establish causal savings from prepaid conversion. Model metrics and financial estimates should be validated through a controlled pilot.

### Example 4: Local LLM-assisted address validation

- **Tool:** Ollama with Qwen 2.5 (3B), integrated into the Streamlit dashboard.
- **Input:** "Station chowk se left, Hanuman Mandir ke saamne", Chennai, Tamil Nadu, 600084.
- **Initial result:** The LLM identified the address as ambiguous and recommended requesting a specific house number or street name.
- **Final action:** The dashboard flagged the order for manual address confirmation before dispatch.
- **Limitation:** The model returned generic missing-information text rather than extracting a verified house number or street name. Human confirmation remains necessary.