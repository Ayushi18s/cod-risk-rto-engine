# Founder Memo: COD RTO Decision System

**Status:** Prototype / historical backtest required before live deployment.

## Executive summary
The system scores COD orders before dispatch and recommends normal dispatch, WhatsApp confirmation, or a prepaid nudge. It is designed as decision support: it does not automatically cancel orders based on a model score.

## Dataset and methodology
The supplied sample contains 2,018 rows and 17 fields. The pipeline normalizes status labels and removes duplicate order IDs. Only orders with final status DELIVERED or RTO are used for supervised training; in-transit orders are excluded. Model performance is reported on a stratified holdout set.

Before presenting this memo, run the app and record the actual cleaned counts, channel/city findings, model metrics and confusion matrix. Do not present exploratory small groups as reliable causal findings.

## Unit economics from assignment assumptions
Expected RTO cost = ₹65 forward shipping + ₹65 return shipping + ₹25 packaging/handling + (8% × ₹180 expected damage) = ₹169.40.

Expected RTO reduction from COD to prepaid = 28% − 4% = 24 percentage points. Expected gross avoided RTO cost per converted order = 24% × ₹169.40 = ₹40.66. With a ₹20 discount, expected net saving is ₹20.66 per converted order, before payment fees and other effects.

## Decision policy
- Low risk: ship as-is.
- Medium risk: offer prepaid conversion.
- High risk or poor address/name/pincode quality: WhatsApp confirmation.
- NO response or unclear response: hold for human review; do not automatically cancel.

## Ops vs marketing trade-off
A stricter policy can reduce RTO exposure but may create friction and lose genuine orders. Measure confirmation rate, prepaid conversion, cancellation rate, delivery success and contribution margin by acquisition source. Do not blacklist a channel or city from small samples.

## Pilot and monitoring
Run in shadow mode first. Compare recommendations against actual outcomes. Then A/B test WhatsApp confirmation and prepaid offers. Monitor weekly: RTO rate, confirmation rate, prepaid conversion, genuine-order cancellation proxy, dispatch delay, complaint rate, and net contribution after discounts and messaging costs.

## Next two weeks
1. Validate data quality and freeze a reproducible training snapshot.
2. Review false positives with operations.
3. Test WhatsApp copy and timing on a small randomized cohort.
4. Compare treatment and control cohorts before scaling.
