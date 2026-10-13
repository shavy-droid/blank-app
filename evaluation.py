"""CSV parsing and deterministic evaluation, independent of the web interface."""

import pandas as pd

CATEGORIES = [
    "ORDER_STATUS", "RETURNS_REFUNDS", "PRODUCT_INFO", "TECH_SUPPORT", "HUMAN_REVIEW"
]

def read_csv_input(source):
    """Preserve literal text (including NA) and leading-zero enquiry IDs."""
    return pd.read_csv(source, dtype=str, keep_default_na=False)


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
    result["reference_risk_conflict"] = (
        result["risk_level"].eq("high") & ~result["expected_label"].eq("HUMAN_REVIEW")
    )
    return result

def agreement_percentage(result):
    """Calculate agreement with references; an empty evaluation is undefined."""
    if result.empty:
        raise ValueError("Cannot calculate agreement for an empty evaluation")
    return 100 * int(result["correct"].sum()) / len(result)
