import polars as pl
import pytest
from src.detector import detect_anomalies_zscore

def test_detect_anomalies_finds_extreme_outlier():
    data = {"metric": [10.0, 10.2, 9.8, 10.1, 9.9, 10.0, 10.3, 9.7, 10.0, 1000.0]}
    df = pl.DataFrame(data)
    df_analyzed, anomalies = detect_anomalies_zscore(df, metric_col="metric", threshold=2.5)

    assert len(anomalies) == 1
    assert anomalies["metric"][0] == 1000.0

def test_detect_anomalies_raises_key_error_on_missing_column():
    df = pl.DataFrame({"valid_col": [1, 2, 3]})
    with pytest.raises(KeyError):
        detect_anomalies_zscore(df, metric_col="missing_col")
