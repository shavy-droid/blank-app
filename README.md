# PilotProof â€” AI Pilot Evaluation Studio

**A working Streamlit prototype for evaluating recorded AI-generated customer enquiry classifications before considering operational adoption.**

**[Try the live application](https://pilotproof.streamlit.app/)**

> **Scope:** This is an educational portfolio prototype using fictional enquiries. It evaluates *previously recorded* AI predictions; it does not call a language model live, automate real customer support, or establish production-level model accuracy.

## The problem

A retailer considering AI to sort incoming customer messages may want to send routine delivery, product and refund enquiries to the appropriate teams while escalating sensitive complaints to a person. An impressive headline accuracy rate is not enough to decide whether such a system is suitable for use: an incorrectly routed delivery enquiry and a missed fraud or safety report have different potential consequences.

PilotProof explores how a business could examine classification agreement, investigate errors and consider human oversight **before** progressing to a controlled AI pilot. Its purpose is decision support, not an automated approval to deploy.

## What the application does

- Loads a built-in **30-enquiry synthetic demonstration** immediately, without requiring visitors to prepare files.
- Alternatively accepts three CSV files: enquiries, provisional reference labels and recorded AI predictions.
- Validates required columns, non-empty fields, unique identifiers, permitted categories, and consistency of enquiry IDs across inputs.
- Joins records by `enquiry_id` rather than assuming CSV rows are in the same order; preserves leading-zero identifiers such as `001`.
- Measures exact **agreement with reference labels**, displays a confusion matrix and lets reviewers inspect individual cases.
- Flags **high-risk escalation misses**: a case annotated `high` for risk but predicted as something other than `HUMAN_REVIEW`.
- Warns when a high-risk reference case has an expected category other than `HUMAN_REVIEW`, without quietly altering its label or score.
- Lets reviewers filter high-risk, ambiguous and mismatched cases, and export per-enquiry evaluation results.
- Presents adoption considerations spanning business strategy, governance and employee oversight.

## How it works

1. **Prepare enquiries.** Each fictional customer message has a unique `enquiry_id`.
2. **Define provisional reference labels.** Each message has an expected category, a risk level, a clarity annotation and a short labelling rationale.
3. **Record model predictions.** ChatGPT was asked in a separate classification exercise to assign one category to each message. Those responses were saved; PilotProof does **not** ask ChatGPT to classify anything in real time.
4. **Compare and review.** Python and pandas validate and join the three inputs, calculate agreement, flag escalation misses and display results in Streamlit.

The five permitted categories are `ORDER_STATUS`, `RETURNS_REFUNDS`, `PRODUCT_INFO`, `TECH_SUPPORT` and `HUMAN_REVIEW`.

**Agreement** = number of exact prediction/reference matches Ã· total cases. An **escalation miss** is defined as `risk_level == "high"` and `predicted_label != "HUMAN_REVIEW"`. These are deliberately simple, transparent rules; neither metric establishes broader model safety.

## Recorded demonstration results

| Measure | Built-in challenge demonstration |
|---|---:|
| Synthetic customer enquiries | 30 |
| Exact matches with provisional reference labels | 30 / 30 |
| Agreement with provisional reference labels | 100% |
| Cases annotated high-risk | 10 |
| High-risk escalation misses under the defined rule | 0 |
| Cases annotated as mixed/ambiguous | 16 |

**Interpretation:** These figures demonstrate agreement on this particular set of examples. They do **not** mean the AI is 100% accurate on real customer enquiries. The sample is small and synthetic; the enquiries and provisional labels were prepared with AI assistance and have not been independently adjudicated. That overlap can create bias. The test does not establish repeatability across different models, prompts or repeated runs.

An earlier separate **40-case preliminary exercise** also returned 40/40 matches against provisional labels. Its original files are not currently part of this repository, so the built-in 30-case demonstration is the directly inspectable example here. The two results should not be presented as independent evidence of production reliability.

## Technology and project development

| Technology | Role |
|---|---|
| Python | Application logic and deterministic evaluation |
| pandas | Reading, validating, joining and analysing tabular data |
| Streamlit | Interactive web interface and visualisations |
| GitHub / GitHub Codespaces | Version control and browser-based development environment |
| Streamlit Community Cloud | Public deployment |
| ChatGPT | AI-assisted coding, synthetic-data preparation and recorded classification experiment |
| OpenAI Codex | Subsequent code review, refactoring and generation of automated tests |
| pytest | Repeatable checks of key evaluation rules |

This was an **AI-assisted development project**, not an independently hand-coded AI model. I selected and implemented the project workflow, ran and reviewed the experiments, tested the application in Codespaces, troubleshot file-matching issues, deployed it publicly and reviewed the subsequent Codex changes. ChatGPT provided substantial coding guidance and generated code; Codex later proposed reliability improvements and tests. The aim was to learn how to implement and critically assess a working AI evaluation workflow.

## Testing and reliability work

A later Codex-assisted revision extracted evaluation logic into `evaluation.py` and added tests in `tests/`. **Codex reported** a successful final test run:

```text
uv run --locked pytest -q
25 passed in 1.05s
```

The tests include shuffled-row matching, preservation of leading zeros, rejection of malformed inputs, a deliberately imperfect **3/4 = 75%** scoring fixture, high-risk escalation misses, conflicting reference/risk annotations, literal text such as `NA`, and basic Streamlit interface behaviour.

The reported automated checks do not replace full end-to-end browser testing of uploaded CSV files, security review or a production evaluation.

## Try your own CSV files

Choose **Evaluate my own CSV files** in the application and upload three files from the same experiment:

| Input | Required CSV columns |
|---|---|
| Customer enquiries | `enquiry_id,enquiry` |
| Reference labels | `enquiry_id,expected_label,risk_level,clarity,label_reason` |
| Recorded AI predictions | `enquiry_id,prompt_version,predicted_label` |

Use `high` or `routine` for `risk_level`, and `mixed` or `clear` for `clarity`. The permitted classification categories are listed above. Predictions must use one prompt version and all three files must contain matching unique enquiry IDs. Input files must be under 2 MB each.

**Privacy:** Please use fictional, public or appropriately authorised non-confidential data only. Do not upload personal, commercially sensitive or regulated customer information to this demonstration.

## Run locally

The project uses `uv` for dependency management. With `uv` installed and the repository cloned:

```bash
uv sync
uv run streamlit run streamlit_app.py
```

To run the automated test suite:

```bash
uv run --locked pytest -q
```

The project currently specifies Python 3.14 or later in `pyproject.toml`.

## Limitations and proposed next steps

**Current limitations:** synthetic and AI-assisted source/reference data; limited sample size; no independent human adjudication of labels; no repeat-run or cross-model comparison; no operational cost, service-quality or fairness measurement; no live customer system integration. A flag is only as reliable as its supplied risk annotation. Exported CSV files also require care if opened in spreadsheet software, because untrusted text can potentially be interpreted as a formula.

Before an organisation relied on this type of evaluation, I would recommend:

1. Agree classification and escalation policies with the people who handle actual customer cases.
2. Independently review the reference labels, particularly sensitive and ambiguous examples.
3. Test larger, representative and previously unseen samples, with repeated runs and category-specific error analysis.
4. Define who handles escalated or disputed cases, how exceptions are monitored and when employees can override a recommendation.
5. Measure actual service quality, review effort, implementation costs and privacy/security controls before making a deployment decision.

**Conclusion:** The demonstration supports a more disciplined discussion about AI adoption. It does **not** justify unsupervised deployment on the strength of an apparent 100% agreement score.

