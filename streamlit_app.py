
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="PilotProof",
    page_icon="🧪",
    layout="wide"
)

st.title("PilotProof")
st.subheader("AI Pilot Evaluation Studio")

st.write(
    "Evaluating the reliability, risks and business "
    "readiness of AI-assisted customer service workflows."
)

st.divider()
st.header("1. Upload Evaluation Data")

enquiry_file = st.file_uploader(
    "Upload customer enquiries",
    type=["csv"],
    key="enquiries"
)

labels_file = st.file_uploader(
    "Upload human reference labels",
    type=["csv"],
    key="labels"
)

if enquiry_file is None or labels_file is None:
    st.info("Upload both CSV files to continue.")
    st.stop()


def load_and_validate(file, required_columns):
    df = pd.read_csv(
        file,
        dtype={"enquiry_id": str}
    )

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    if df.empty:
        st.error("One of the uploaded files is empty.")
        st.stop()

    if df["enquiry_id"].isna().any():
        st.error("Some enquiry IDs are missing.")
        st.stop()

    df["enquiry_id"] = df["enquiry_id"].str.strip()

    if df["enquiry_id"].eq("").any():
        st.error("Some enquiry IDs are blank.")
        st.stop()

    if df["enquiry_id"].duplicated().any():
        st.error("Duplicate enquiry IDs were found.")
        st.stop()

    return df


try:
    enquiries = load_and_validate(
        enquiry_file,
        ["enquiry_id", "enquiry"]
    )

    labels = load_and_validate(
        labels_file,
        [
            "enquiry_id",
            "expected_label",
            "risk_level",
            "clarity",
            "label_reason"
        ]
    )

except Exception as error:
    st.error(f"Unable to read the files: {error}")
    st.stop()

if (
    enquiries["enquiry"].isna().any()
    or enquiries["enquiry"].astype(str).str.strip().eq("").any()
):
    st.error("Some customer enquiries are missing or blank.")
    st.stop()

valid_categories = [
    "ORDER_STATUS",
    "RETURNS_REFUNDS",
    "PRODUCT_INFO",
    "TECH_SUPPORT",
    "HUMAN_REVIEW"
]

if (
    labels["expected_label"].isna().any()
    or not labels["expected_label"].isin(valid_categories).all()
):
    st.error("The reference file contains an invalid category.")
    st.stop()

combined = enquiries.merge(
    labels,
    on="enquiry_id",
    how="outer",
    validate="one_to_one",
    indicator=True
)

if not combined["_merge"].eq("both").all():
    st.error(
        "Some enquiry IDs do not match between the two files."
    )
    st.dataframe(
        combined.loc[
            combined["_merge"] != "both",
            ["enquiry_id", "_merge"]
        ]
    )
    st.stop()

combined = combined.drop(columns=["_merge"])

st.success("Both files uploaded and matched successfully!")

st.divider()
st.header("2. Dataset Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Enquiries", len(combined))

with col2:
    st.metric(
        "Categories",
        combined["expected_label"].nunique()
    )

with col3:
    st.metric(
        "Human Review Cases",
        (combined["expected_label"] == "HUMAN_REVIEW").sum()
    )

st.subheader("Category Distribution")

category_counts = (
    combined["expected_label"]
    .value_counts()
    .sort_index()
)

st.bar_chart(category_counts)

st.subheader("Enquiries and Reference Labels")

st.dataframe(
    combined[
        [
            "enquiry_id",
            "enquiry",
            "expected_label",
            "risk_level",
            "clarity",
            "label_reason"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()
st.header("3. Cases Requiring Label Review")

mixed_cases = combined[
    combined["clarity"] == "mixed"
]

st.warning(
    f"{len(mixed_cases)} enquiries have potentially "
    "ambiguous reference labels."
)

st.dataframe(
    mixed_cases[
        [
            "enquiry_id",
            "enquiry",
            "expected_label",
            "label_reason"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.caption(
    "This is a synthetic evaluation dataset. "
    "Reference labels are provisional and require "
    "human review. No AI model has been evaluated yet."
)
# FEATURE 3 — PASTE BELOW THE EXISTING PILOTPROOF CODE.
# This is an add-on, not a standalone Streamlit app.

st.divider()
st.header("4. AI Classification Evaluation")

prediction_file = st.file_uploader(
    "Upload AI predictions (CSV)",
    type=["csv"],
    key="predictions"
)

if prediction_file is not None:
    try:
        predictions = pd.read_csv(
            prediction_file,
            dtype={"enquiry_id": str, "prompt_version": str, "predicted_label": str}
        )
    except Exception as error:
        st.error(f"Could not read predictions CSV: {error}")
        st.stop()

    needed = ["enquiry_id", "prompt_version", "predicted_label"]
    missing = [col for col in needed if col not in predictions.columns]

    if missing:
        st.error(f"Missing prediction columns: {missing}")
        st.stop()

    if predictions.empty or predictions[needed].isna().any().any():
        st.error("The predictions file is empty or contains missing values.")
        st.stop()

    for col in needed:
        predictions[col] = predictions[col].str.strip()

    if predictions[needed].eq("").any().any():
        st.error("The predictions file contains blank fields.")
        st.stop()

    if predictions["enquiry_id"].duplicated().any():
        st.error("The predictions file contains duplicate enquiry IDs.")
        st.stop()

    if not predictions["predicted_label"].isin(valid_categories).all():
        st.error("The predictions file contains an invalid category.")
        st.stop()

    if predictions["prompt_version"].nunique() != 1:
        st.error("Upload predictions from only one prompt version at a time.")
        st.stop()

    expected_ids = set(combined["enquiry_id"])
    received_ids = set(predictions["enquiry_id"])

    if expected_ids != received_ids:
        st.error(
            f"IDs do not match: {len(expected_ids - received_ids)} missing; "
            f"{len(received_ids - expected_ids)} unexpected. "
            "Check that you uploaded the prediction file for this dataset."
        )
        st.stop()

    results = combined.merge(
        predictions[needed],
        on="enquiry_id",
        how="left",
        validate="one_to_one"
    )
    results["correct"] = (
        results["expected_label"] == results["predicted_label"]
    )

    accuracy = 100 * results["correct"].mean()
    correct_count = int(results["correct"].sum())
    high_risk = results[results["risk_level"] == "high"]
    high_risk_misses = int(
        (high_risk["predicted_label"] != "HUMAN_REVIEW").sum()
    )

    st.success("Predictions validated and matched to reference labels.")
    st.caption(
        f"Prompt version: {predictions['prompt_version'].iloc[0]} | "
        "Reference labels are provisional and require human review."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Accuracy", f"{accuracy:.1f}%")
    c2.metric("Correct predictions", f"{correct_count}/{len(results)}")
    c3.metric("High-risk cases not escalated", high_risk_misses)

    st.subheader("Expected versus predicted categories")
    matrix = pd.crosstab(
        results["expected_label"],
        results["predicted_label"],
        rownames=["Expected"],
        colnames=["Predicted"],
        dropna=False
    )
    st.dataframe(matrix, use_container_width=True)

    st.subheader("Classification mismatches")
    mistakes = results.loc[
        ~results["correct"],
        ["enquiry_id", "enquiry", "expected_label", "predicted_label", "risk_level"]
    ]

    if mistakes.empty:
        st.success("No mismatches against these reference labels.")
    else:
        st.dataframe(mistakes, use_container_width=True, hide_index=True)

    st.download_button(
        "Download per-enquiry evaluation",
        data=results.to_csv(index=False).encode("utf-8"),
        file_name="pilotproof_evaluation_results.csv",
        mime="text/csv"
    )

    st.warning(
        "A high score on this small, sorted synthetic dataset does NOT "
        "establish real-world reliability. We will also test randomly "
        "ordered, unseen and more challenging enquiries."
    )
