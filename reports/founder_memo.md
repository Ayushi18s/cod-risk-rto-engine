# Founder Memo: COD Risk & RTO Decision Engine

**Recommendation:** Launch a controlled, human-in-the-loop pilot of the COD risk engine. Do not automatically cancel orders based on model scores.

## 1. Key findings from the historical dataset

After removing 30 duplicate order IDs, normalizing status labels and excluding the in-transit order, the analysis contains **1,987 labeled orders: 1,422 delivered and 565 RTO**. The observed RTO rate is **28.43%**.

Three important findings:

**Customer history is a useful risk signal.**
- No prior RTO: 27.2% RTO rate (1,845 orders).
- One prior RTO: 35.2% (108 orders).
- Two prior RTOs: 76.5% (34 orders).

The two-prior-RTO group is small. Use this signal to trigger confirmation, not automatic rejection.

**Acquisition source has different observed RTO rates.**
- Meta Ads: 31.3% (779 orders).
- Direct: 22.7% (256 orders).
- Google Ads: 28.0% (246 orders).
- WhatsApp Broadcast: 26.5% (272 orders).
- Instagram Organic: 29.4% (235 orders).
- Influencer: 26.6% (229 orders).

These are observational differences, not proof that a channel causes RTO. Marketing decisions should account for customer and geographic mix.

**Geographic risk varies substantially.**
- Gorakhpur: 63.0% (46 orders).
- Darbhanga: 58.1% (62 orders).
- Sagar: 50.9% (55 orders).
- Patna: 47.5% (80 orders).
- Delhi: 21.5% (246 orders).
- Mumbai: 17.8% (219 orders).
- Pune: 18.1% (171 orders).

Use these findings to prioritize address verification and courier review. Do not blacklist cities based on small samples.

**Data-quality note:** The dataset's mean order value is approximately ₹920, compared with the assignment's stated AOV of ₹649. Use ₹649 for the assignment's financial assumptions and investigate the discrepancy before forecasting.

## 2. Model performance and decision policy

The current Random Forest baseline reports the following held-out test metrics:

- ROC-AUC: **0.715**
- Accuracy: **73.64%**
- RTO recall: **48.94%**
- Test records: **497**

This model is useful for risk ranking, but it misses approximately half of RTO cases at the default classification threshold. It is not suitable as a standalone cancellation mechanism.

The proposed four-way policy is:

1. **Ship as-is:** Low risk, with no critical data-quality flags.
2. **Prepaid nudge:** Medium risk; offer a small prepaid discount.
3. **WhatsApp confirmation:** High risk or a non-critical address/name concern.
4. **Hold / manual review:** Severe data-quality issues, such as an invalid pincode or combined name/address concerns.

A missing response or unclear WhatsApp reply after 24 hours should lead to manual review, not silent cancellation.

## 3. Unit economics and counterfactual scenario

Using the assignment assumptions:

Expected RTO cost = ₹65 forward shipping + ₹65 return shipping + ₹25 packaging/handling + (8% × ₹180 expected damage) = **₹169.40**.

The assumed RTO-rate difference between COD and prepaid is 28% − 4% = 24 percentage points.

Expected gross RTO cost avoided per successful prepaid conversion:

24% × ₹169.40 = **₹40.66**.

After a ₹20 prepaid discount:

**Estimated net benefit = ₹20.66 per successful conversion**, before payment processing fees, messaging costs and other behavioral effects.

### Illustrative last-month counterfactual

Assume 3,000 monthly orders and 55% COD, giving 1,650 COD orders. If 10% of those COD orders had converted to prepaid:

- Prepaid conversions: 165.
- Estimated gross RTO cost avoided: 165 × ₹40.66 = approximately ₹6,709.
- Discounts: 165 × ₹20 = ₹3,300.
- Estimated net benefit: approximately **₹3,408**.

This is a scenario, not a measured saving. The supplied historical data does not contain actual WhatsApp treatment responses or prepaid-conversion outcomes, so the true causal impact cannot be established from this sample alone.

The assignment's delivered gross margin on ₹649 is 62% × ₹649 = **₹402.38**. This is the approximate contribution opportunity at risk when a genuine order is wrongly cancelled, before any additional customer lifetime value.

The ₹300+ Meta CAC is already incurred by the time the pre-shipment decision is made. Treat it as acquisition exposure, not an additional RTO shipping cost.

## 4. Operations versus Marketing

Operations should own address quality, confirmation workflows, dispatch delays and courier performance. Marketing should help test prepaid offer framing and conversion.

An overly strict policy may reduce RTOs but also delay genuine orders and increase cancellations. Review outcomes jointly by acquisition source, geography, courier and customer history. Do not reduce marketing investment solely because a channel has a higher observed RTO rate.

## 5. Risks and monitoring

Run the engine in shadow mode before applying decisions to live orders. Then conduct a small randomized pilot.

Monitor:
- RTO and delivery rates by decision bucket.
- WhatsApp response and confirmation rates.
- COD-to-prepaid conversion rate.
- Genuine-order cancellation and complaint rates.
- Dispatch delays.
- Discount, messaging and net contribution costs.
- False positives identified through manual review.

Keep human override and a decision audit trail. The current WhatsApp workflow is a simulator and does not send real messages.

## 6. Next two weeks

1. Reconcile duplicate IDs, missing city/pincode values and the AOV discrepancy.
2. Review a sample of high-risk and held orders with Operations.
3. Run a small randomized WhatsApp confirmation and prepaid-offer pilot.
4. Compare incremental net contribution and customer friction before scaling.
