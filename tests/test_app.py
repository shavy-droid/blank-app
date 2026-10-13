"""Exercise the public demo and controls using Streamlit's test runner."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_demo_metrics_filters_and_upload_screen():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'streamlit_app.py')).run(timeout=30)
    assert not app.exception
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics == {
        'Agreement with references': '100.0%',
        'Matching classifications': '30/30',
        'High-risk cases': '10',
        'High-risk escalation misses': '0',
    }
    assert len(app.dataframe[0].value) == 30
    app.selectbox[0].select('High-risk only').run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 10
    app.selectbox[0].select('Ambiguous only').run()
    assert len(app.dataframe[0].value) == 16
    app.selectbox[0].select('Mismatches only').run()
    assert app.dataframe[0].value.empty
    app.radio[0].set_value('Evaluate my own CSV files').run()
    assert not app.exception
    assert len(app.get('file_uploader')) == 3
    assert any('Upload all three files' in info.value for info in app.info)
