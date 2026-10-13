"""Small fictional cases; recorded experimental data is never modified."""
from io import StringIO

import pandas as pd
import pytest

from evaluation import agreement_percentage, clean_and_validate, read_csv_input


@pytest.fixture
def tables():
    enquiries = read_csv_input(StringIO(
        'enquiry_id,enquiry\n001,Where is my order?\n002,I need a refund\n003,Report a safety issue\n004,Checkout is broken\n'
    ))
    labels = pd.DataFrame({
        'enquiry_id': ['001', '002', '003', '004'],
        'expected_label': ['ORDER_STATUS', 'RETURNS_REFUNDS', 'HUMAN_REVIEW', 'TECH_SUPPORT'],
        'risk_level': ['routine', 'routine', 'high', 'routine'],
        'clarity': ['clear'] * 4,
        'label_reason': ['Fictional test reference'] * 4,
    })
    predictions = pd.DataFrame({
        'enquiry_id': ['001', '002', '003', '004'],
        'prompt_version': ['test_only'] * 4,
        'predicted_label': ['ORDER_STATUS', 'RETURNS_REFUNDS', 'HUMAN_REVIEW', 'PRODUCT_INFO'],
    })
    return enquiries, labels, predictions


def test_matching_uses_ids_and_preserves_leading_zeros(tables):
    enquiries, labels, predictions = tables
    result = clean_and_validate(enquiries, labels.iloc[::-1], predictions.iloc[[2, 0, 3, 1]])
    assert result.enquiry_id.tolist() == ['001', '002', '003', '004']
    assert result.predicted_label.tolist() == predictions.predicted_label.tolist()
    assert result.correct.tolist() == [True, True, True, False]


@pytest.mark.parametrize('table_index', [0, 1, 2])
@pytest.mark.parametrize('problem', ['missing_column', 'duplicate_id', 'blank', 'missing_value'])
def test_rejects_invalid_structure(tables, table_index, problem):
    frames = list(tables)
    frame = frames[table_index].copy()
    column = frame.columns[1]
    if problem == 'missing_column':
        frame = frame.drop(columns=column)
        message = 'missing columns'
    elif problem == 'duplicate_id':
        frame.loc[1, 'enquiry_id'] = ' 001 '
        message = 'IDs must be unique'
    else:
        frame.loc[0, column] = '   ' if problem == 'blank' else None
        message = 'blank values' if problem == 'blank' else 'missing values'
    frames[table_index] = frame
    with pytest.raises(ValueError, match=message):
        clean_and_validate(*frames)


@pytest.mark.parametrize('table_index,column', [(1, 'expected_label'), (2, 'predicted_label')])
def test_rejects_unknown_category(tables, table_index, column):
    tables[table_index].loc[0, column] = 'UNKNOWN'
    with pytest.raises(ValueError, match='unknown category'):
        clean_and_validate(*tables)


def test_three_of_four_matches_is_75_percent(tables):
    result = clean_and_validate(*tables)
    assert result.correct.sum() == 3
    assert agreement_percentage(result) == 75.0


def test_high_risk_escalation_miss_is_separate_from_routine_error(tables):
    tables[2].loc[2, 'predicted_label'] = 'ORDER_STATUS'
    result = clean_and_validate(*tables)
    assert result.escalation_miss.tolist() == [False, False, True, False]
    tables[2].loc[2, 'predicted_label'] = 'HUMAN_REVIEW'
    assert not clean_and_validate(*tables).escalation_miss.any()


def test_conflicting_reference_is_flagged_without_changing_scores(tables):
    tables[1].loc[0, 'risk_level'] = 'high'
    result = clean_and_validate(*tables)
    assert result.reference_risk_conflict.tolist() == [True, False, False, False]
    assert result.loc[0, 'expected_label'] == 'ORDER_STATUS'
    assert result.loc[0, 'correct']
    assert result.loc[0, 'escalation_miss']
    assert agreement_percentage(result) == 75.0


@pytest.mark.parametrize('text', ['NA', 'N/A', 'NULL', 'null'])
def test_literal_customer_text_is_preserved(tables, text):
    tables = list(tables)
    tables[0] = read_csv_input(StringIO(
        'enquiry_id,enquiry\n001,' + text + '\n002,Refund\n003,Safety\n004,Checkout\n'
    ))
    assert clean_and_validate(*tables).loc[0, 'enquiry'] == text


@pytest.mark.parametrize('text', ['', '   '])
def test_blank_customer_csv_text_is_rejected(tables, text):
    tables = list(tables)
    tables[0] = read_csv_input(StringIO(
        'enquiry_id,enquiry\n001,' + text + '\n002,Refund\n003,Safety\n004,Checkout\n'
    ))
    with pytest.raises(ValueError, match='blank values'):
        clean_and_validate(*tables)
