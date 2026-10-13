import polars as pl

def detect_anomalies_zscore(
    df: pl.DataFrame,
    metric_col: str,
    threshold: float = 3.0
) -> tuple[pl.DataFrame, pl.DataFrame]:
    if metric_col not in df.columns:
        raise KeyError(f"'{metric_col}' sütunu veri setinde bulunamadı.")

    mean_val = df[metric_col].mean()
    std_val = df[metric_col].std()

    if std_val == 0 or std_val is None:
        raise ValueError("Standart sapma sıfır veya tanımsız; Z-Score hesaplanamaz.")

    df_analyzed = df.with_columns(
        ((pl.col(metric_col) - mean_val) / std_val).abs().alias("z_score")
    )

    anomalies = df_analyzed.filter(pl.col("z_score") >= threshold)
    return df_analyzed, anomalies
