"""PilotProof — AI Pilot Evaluation Studio.

A graduate portfolio prototype for evaluating recorded AI classification outputs.
The built-in demo uses 30 synthetic enquiries, provisional reference labels,
and predictions from a recorded ChatGPT classification experiment.

This app DOES NOT call a live language model, and scores only agreement with
reference labels, not real-world production accuracy.
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="PilotProof | AI Pilot Evaluation Studio", page_icon="🧪", layout="wide")

CATEGORIES = [
    "ORDER_STATUS", "RETURNS_REFUNDS", "PRODUCT_INFO", "TECH_SUPPORT", "HUMAN_REVIEW"
]

# Demo evidence is embedded to make the public example usable without uploads.
# Entries were copied from the 30-case synthetic challenge dataset,
# draft reference labels, and *recorded* baseline_challenge model predictions.
# Reference labels remain provisional; they are not externally validated.
DEMO_ROWS = [{'enquiry_id': '101',
  'enquiry': "Do you expect to restock the blue medium joggers next month? I haven't ordered yet.",
  'expected_label': 'PRODUCT_INFO',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Stock availability before purchase',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'PRODUCT_INFO'},
 {'enquiry_id': '102',
  'enquiry': "I'm reporting repeated threatening messages allegedly sent by a delivery driver. I don't "
             'feel safe contacting the driver again.',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'mixed',
  'label_reason': 'Potential harassment or personal safety issue requires human intervention',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '103',
  'enquiry': 'You sent the wrong colour and I want my money back rather than a replacement.',
  'expected_label': 'RETURNS_REFUNDS',
  'risk_level': 'routine',
  'clarity': 'mixed',
  'label_reason': "Customer's primary requested outcome is a refund",
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'RETURNS_REFUNDS'},
 {'enquiry_id': '104',
  'enquiry': 'Your chatbot used discriminatory language towards me and I want a manager to investigate '
             'it, not an automated reply.',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'mixed',
  'label_reason': 'Serious discrimination complaint with explicit human escalation',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '105',
  'enquiry': "The trainers were delivered, but a seam split on first use. I'd like an exchange under "
             'the returns policy.',
  'expected_label': 'RETURNS_REFUNDS',
  'risk_level': 'routine',
  'clarity': 'mixed',
  'label_reason': 'Customer is asking for an exchange, not reporting injury or an urgent hazard',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'RETURNS_REFUNDS'},
 {'enquiry_id': '106',
  'enquiry': 'I want to raise a formal complaint about being refused service because of my disability. '
             'Please have someone contact me.',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'clear',
  'label_reason': 'Serious allegation of discrimination and explicit human escalation',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '107',
  'enquiry': "The return portal freezes on the confirmation screen. I can't submit my return request "
             "even though I'm within the window.",
  'expected_label': 'TECH_SUPPORT',
  'risk_level': 'routine',
  'clarity': 'mixed',
  'label_reason': 'Technical malfunction is the immediate blocker; return request is context',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'TECH_SUPPORT'},
 {'enquiry_id': '108',
  'enquiry': "The drawstring fitting on a hoodie came loose and nearly struck my child's eye. Who can "
             'investigate the safety issue?',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'mixed',
  'label_reason': 'Potential product safety issue involving a child requires escalation',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '109',
  'enquiry': 'The delivery email lists two packages but only one has a tracking number. Where is the '
             'second parcel?',
  'expected_label': 'ORDER_STATUS',
  'risk_level': 'routine',
  'clarity': 'mixed',
  'label_reason': 'Status of an existing split delivery',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'ORDER_STATUS'},
 {'enquiry_id': '110',
  'enquiry': "Is the 'oversized' tee cut wider only, or is it also longer than your regular tee?",
  'expected_label': 'PRODUCT_INFO',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Product sizing/fit details',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'PRODUCT_INFO'},
 {'enquiry_id': '111',
  'enquiry': 'I believe a staff member shared my home address with another customer. I need your '
             'privacy team to investigate.',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'mixed',
  'label_reason': 'Potential unauthorised personal-data disclosure',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '112',
  'enquiry': 'I can see my basket but clicking Pay shows error 502 every time. No order has been '
             'placed.',
  'expected_label': 'TECH_SUPPORT',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Checkout technical failure, no existing order',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'TECH_SUPPORT'},
 {'enquiry_id': '113',
  'enquiry': "My return was approved last week but the refund hasn't reached my bank. Can you check the "
             'payment status?',
  'expected_label': 'RETURNS_REFUNDS',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Refund status enquiry',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'RETURNS_REFUNDS'},
 {'enquiry_id': '114',
  'enquiry': 'Can you tell me if the charcoal overshirt comes in a tall fit, or is it standard length?',
  'expected_label': 'PRODUCT_INFO',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Pre-purchase product fit information',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'PRODUCT_INFO'},
 {'enquiry_id': '115',
  'enquiry': 'I was charged after I cancelled my order within the stated cancellation window. Please '
             'arrange a refund.',
  'expected_label': 'RETURNS_REFUNDS',
  'risk_level': 'routine',
  'clarity': 'mixed',
  'label_reason': 'Billing issue framed as a routine refund request with no fraud indication',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'RETURNS_REFUNDS'},
 {'enquiry_id': '116',
  'enquiry': 'Please provide a copy of all personal data you hold on me and tell me how I can have it '
             'erased.',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'clear',
  'label_reason': 'Data-rights request should be routed to an authorised human privacy process',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '117',
  'enquiry': "My sweater arrived two days ago and the sleeves are too short. I'd like to exchange it "
             'for a larger size.',
  'expected_label': 'RETURNS_REFUNDS',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Customer requests an exchange following delivery',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'RETURNS_REFUNDS'},
 {'enquiry_id': '118',
  'enquiry': 'Do the white graphic tees use water-based printing or heat-transfer vinyl?',
  'expected_label': 'PRODUCT_INFO',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Product manufacturing and materials enquiry',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'PRODUCT_INFO'},
 {'enquiry_id': '119',
  'enquiry': 'Order C549 has a dispatch notice but no courier tracking link. How do I find the '
             'shipment?',
  'expected_label': 'ORDER_STATUS',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Existing order tracking request',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'ORDER_STATUS'},
 {'enquiry_id': '120',
  'enquiry': 'My parcel is shown as delivered, but the concierge says nothing arrived. Can you help '
             'locate order C521?',
  'expected_label': 'ORDER_STATUS',
  'risk_level': 'routine',
  'clarity': 'mixed',
  'label_reason': 'Primary request is locating a specific delivery, not requesting a refund',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'ORDER_STATUS'},
 {'enquiry_id': '121',
  'enquiry': 'Before I buy the coat, is the lining wool or synthetic, and is it machine washable?',
  'expected_label': 'PRODUCT_INFO',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Pre-purchase material and care information',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'PRODUCT_INFO'},
 {'enquiry_id': '122',
  'enquiry': 'I developed a severe skin reaction after wearing your new jacket and have needed medical '
             'attention. Please alert your product safety team.',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'mixed',
  'label_reason': 'Possible product safety issue involving injury or health consequence',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '123',
  'enquiry': "The promo-code box disappears when I enter my postcode at checkout, so I can't finish "
             'paying.',
  'expected_label': 'TECH_SUPPORT',
  'risk_level': 'routine',
  'clarity': 'mixed',
  'label_reason': 'Checkout interface problem takes priority over pricing',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'TECH_SUPPORT'},
 {'enquiry_id': '124',
  'enquiry': "Someone accessed my account and placed an order to an address I've never used. Please "
             'secure the account and contact me.',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'mixed',
  'label_reason': 'Potential account takeover and fraudulent transaction',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '125',
  'enquiry': 'Can you confirm whether order C538 can still arrive on Friday, or whether the carrier has '
             'changed the date?',
  'expected_label': 'ORDER_STATUS',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Delivery timing for an existing order',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'ORDER_STATUS'},
 {'enquiry_id': '126',
  'enquiry': "Tracking for order C526 hasn't moved for five days. Has it actually been dispatched?",
  'expected_label': 'ORDER_STATUS',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Order dispatch and tracking status',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'ORDER_STATUS'},
 {'enquiry_id': '127',
  'enquiry': 'I cannot log in: the password reset link always says expired as soon as I open it.',
  'expected_label': 'TECH_SUPPORT',
  'risk_level': 'routine',
  'clarity': 'clear',
  'label_reason': 'Account access functionality failure',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'TECH_SUPPORT'},
 {'enquiry_id': '128',
  'enquiry': 'I received an email allegedly from you asking me to upload a photograph of my passport '
             'through an unfamiliar link. Is this genuine?',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'mixed',
  'label_reason': 'Suspicious identity-document request raises fraud/privacy risk',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'},
 {'enquiry_id': '129',
  'enquiry': 'The size selector is greyed out on your mobile site, but the same product shows available '
             'on desktop.',
  'expected_label': 'TECH_SUPPORT',
  'risk_level': 'routine',
  'clarity': 'mixed',
  'label_reason': 'Broken interface element, despite appearance of stock problem',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'TECH_SUPPORT'},
 {'enquiry_id': '130',
  'enquiry': 'A message claiming to be your company asked for my card PIN to release my order, and I '
             'already replied. Please investigate urgently.',
  'expected_label': 'HUMAN_REVIEW',
  'risk_level': 'high',
  'clarity': 'mixed',
  'label_reason': 'Suspected phishing and financial-data compromise overrides delivery issue',
  'prompt_version': 'baseline_challenge',
  'predicted_label': 'HUMAN_REVIEW'}]


def clean_and_validate(enquiries, labels, predictions):
    """Return a matched result table; reject invalid or mismatched CSV inputs."""
    requirements = (
        (enquiries, ["enquiry_id", "enquiry"], "Customer enquiries"),
        (labels, ["enquiry_id", "expected_label", "risk_level", "clarity", "label_reason"], "Reference labels"),
        (predictions, ["enquiry_id", "prompt_version", "predicted_label"], "AI predictions"),
    )
    cleaned = []
    for frame, required, name in requirements:
        missing = [col for col in required if col not in frame.columns]
        if missing:
            raise ValueError(f"{name}: missing columns: {', '.join(missing)}")
        if frame.empty:
            raise ValueError(f"{name}: file is empty")
        frame = frame[required].copy()
        for col in required:
            if frame[col].isna().any():
                raise ValueError(f"{name}: missing values in '{col}'")
            frame[col] = frame[col].astype(str).str.strip()
            if frame[col].eq("").any():
                raise ValueError(f"{name}: blank values in '{col}'")
        if frame["enquiry_id"].duplicated().any():
            raise ValueError(f"{name}: enquiry IDs must be unique")
        cleaned.append(frame)

    e, l, p = cleaned
    if not l["expected_label"].isin(CATEGORIES).all():
        raise ValueError("Reference labels include an unknown category")
    if not p["predicted_label"].isin(CATEGORIES).all():
        raise ValueError("AI predictions include an unknown category")
    if not l["risk_level"].isin(["high", "routine"]).all():
        raise ValueError("Reference labels: risk_level must be 'high' or 'routine'")
    if not l["clarity"].isin(["mixed", "clear"]).all():
        raise ValueError("Reference labels: clarity must be 'mixed' or 'clear'")
    if p["prompt_version"].nunique() != 1:
        raise ValueError("Upload predictions from only one prompt version")
    e_ids, l_ids, p_ids = [set(frame["enquiry_id"]) for frame in (e, l, p)]
    if e_ids != l_ids or e_ids != p_ids:
        raise ValueError("Enquiry IDs do not match across all three files. Use files from the same experiment.")

    result = (e.merge(l, on="enquiry_id", validate="one_to_one")
                .merge(p, on="enquiry_id", validate="one_to_one"))
    result["correct"] = result["expected_label"].eq(result["predicted_label"])
    result["escalation_miss"] = (
        result["risk_level"].eq("high") & ~result["predicted_label"].eq("HUMAN_REVIEW")
    )
    return result


def render_evaluation(result, demo_mode):
    total = len(result)
    right = int(result["correct"].sum())
    missed = int(result["escalation_miss"].sum())
    high = int(result["risk_level"].eq("high").sum())

    st.subheader("Evaluation results")
    a, b, c, d = st.columns(4)
    a.metric("Agreement with references", f"{100 * right / total:.1f}%")
    b.metric("Matching classifications", f"{right}/{total}")
    c.metric("High-risk cases", high)
    d.metric("High-risk escalation misses", missed)

    if missed:
        st.error("One or more proposed high-risk cases were not routed to human review. Investigate these before piloting.")
    else:
        st.info("No high-risk escalation misses were detected in this test set. This does not establish real-world safety.")

    st.warning(
        "These figures measure agreement with provisional labels on a small synthetic dataset. "
        "They are NOT a verified production accuracy rate or an approval to deploy the AI."
    )

    tab1, tab2, tab3 = st.tabs(["Review individual cases", "Error analysis", "Adoption considerations"])
    with tab1:
        risk_choice = st.selectbox("Show cases", ["All", "High-risk only", "Ambiguous only", "Mismatches only"])
        filtered = result
        if risk_choice == "High-risk only":
            filtered = result[result["risk_level"].eq("high")]
        elif risk_choice == "Ambiguous only":
            filtered = result[result["clarity"].eq("mixed")]
        elif risk_choice == "Mismatches only":
            filtered = result[~result["correct"]]
        st.dataframe(
            filtered[["enquiry_id", "enquiry", "expected_label", "predicted_label", "risk_level", "clarity", "correct", "label_reason"]],
            use_container_width=True, hide_index=True
        )
        st.caption("Filtering helps reviewers inspect sensitive or borderline classifications, not just the overall percentage.")

    with tab2:
        st.markdown("**Confusion matrix** — rows show reference labels, columns show recorded AI predictions.")
        matrix = pd.crosstab(result["expected_label"], result["predicted_label"])
        matrix = matrix.reindex(index=CATEGORIES, columns=CATEGORIES, fill_value=0)
        st.dataframe(matrix, use_container_width=True)
        failures = result[~result["correct"]]
        if failures.empty:
            st.success("No mismatches were detected against these reference labels.")
        else:
            st.markdown("**Cases to investigate**")
            st.dataframe(failures[["enquiry_id", "enquiry", "expected_label", "predicted_label", "risk_level"]],
                         use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("""
**Preliminary assessment: further validation required.**

- **AI strategy:** The idea of automating enquiry routing is plausible, but the business case has not been quantified with real staff time, costs or customer outcomes.
- **AI governance:** Before any pilot, agree escalation rules, review reference labels independently, test on representative unseen traffic and document error handling.
- **Workforce transformation:** Keep a person responsible for urgent and disputed cases; train staff on when and how to override AI routing.
- **Decision:** These results justify investigating a controlled pilot, **not** unsupervised deployment.

The tool does not make legal-compliance determinations, provide real-time model inference or prove that a business will save money.
""")

    st.download_button(
        "Download per-enquiry evaluation CSV",
        result.to_csv(index=False).encode("utf-8"),
        file_name="pilotproof_demo_evaluation.csv" if demo_mode else "pilotproof_uploaded_evaluation.csv",
        mime="text/csv"
    )


st.title("🧪 PilotProof")
st.subheader("AI Pilot Evaluation Studio")
st.write("Assess recorded AI classification results before deciding whether a customer-enquiry routing pilot deserves further testing.")
st.caption("Portfolio prototype | Responsible AI evaluation | No real customer data | No live AI API calls")

st.divider()
mode = st.radio("Choose how to explore PilotProof", ["Explore built-in demonstration", "Evaluate my own CSV files"], horizontal=True)

if mode == "Explore built-in demonstration":
    st.success("Ready to explore: 30 synthetic challenge enquiries and recorded baseline AI predictions are preloaded.")
    st.markdown("**What is this example?** A fictional clothing retailer is assessing whether an AI could sort routine enquiries while escalating sensitive ones. The data and reference labels were AI-assisted; the classification predictions were produced in a separate ChatGPT experiment and recorded, not generated live by this app.")
    demo = pd.DataFrame(DEMO_ROWS)
    enquiries = demo[["enquiry_id", "enquiry"]]
    labels = demo[["enquiry_id", "expected_label", "risk_level", "clarity", "label_reason"]]
    predictions = demo[["enquiry_id", "prompt_version", "predicted_label"]]
    st.caption("Experiment: baseline_challenge | 30 cases | 10 labelled high-risk | 16 labelled ambiguous")
else:
    st.subheader("Upload evaluation data")
    st.write("Supply three CSV files from the *same* test run. Preserve leading zeros in IDs. Do not upload confidential customer data.")
    q1 = st.file_uploader("1. Customer enquiries — enquiry_id,enquiry", type="csv", key="enquiries")
    q2 = st.file_uploader("2. Reference labels — expected_label,risk_level,clarity,label_reason", type="csv", key="labels")
    q3 = st.file_uploader("3. Recorded AI predictions — prompt_version,predicted_label", type="csv", key="predictions")
    if not (q1 and q2 and q3):
        st.info("Upload all three files to begin the evaluation.")
        st.stop()
    for f in (q1, q2, q3):
        if f.size > 2_000_000:
            st.error("Please use CSV files smaller than 2 MB for this demonstration.")
            st.stop()
    try:
        enquiries = pd.read_csv(q1, dtype={"enquiry_id": str})
        labels = pd.read_csv(q2, dtype={"enquiry_id": str})
        predictions = pd.read_csv(q3, dtype={"enquiry_id": str})
    except Exception as error:
        st.error(f"Cannot read the CSV file(s): {error}")
        st.stop()

try:
    results = clean_and_validate(enquiries, labels, predictions)
except ValueError as error:
    st.error(str(error))
    st.stop()

st.divider()
render_evaluation(results, demo_mode=(mode == "Explore built-in demonstration"))

with st.expander("About this project and evaluation methodology"):
    st.markdown("""
**Purpose:** Demonstrate how to validate CSV inputs, match AI predictions against reference labels, examine category errors and consider human-oversight requirements.

**Methods:** Python, pandas and Streamlit perform deterministic validation and analysis. A separate ChatGPT classification experiment provided the demo predictions. ChatGPT and AI-assisted programming support were used during development. The running application itself **does not classify enquiries using AI**.

**Evidence:** The initial 40-case synthetic baseline and a separate 30-case challenge both achieved 100% agreement against their draft reference labels. This built-in demo uses the latter. The labels were AI-assisted and lack independent expert adjudication; the test cases are not representative of real customer enquiries.

**Limitations:** Small synthetic samples, potentially biased or ambiguous reference labels, unknown reproducibility across model runs, no measured time savings, no fairness assurance and no independent field test.

**Privacy:** Use fictional or suitably authorised non-confidential datasets only. File uploads are processed in the app session; this prototype is not an approved system for processing sensitive data.
""")
