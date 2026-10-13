import random
from datetime import datetime, timedelta
import polars as pl

def generate_telemetry(num_records: int = 10000, anomaly_rate: float = 0.02) -> pl.DataFrame:
    base_time = datetime.now()
    timestamps = [base_time + timedelta(seconds=i * 5) for i in range(num_records)]
    device_ids = [f"sensor_{random.randint(1, 8):02d}" for _ in range(num_records)]
    values = [random.gauss(45.0, 4.0) for _ in range(num_records)]

    num_anomalies = max(1, int(num_records * anomaly_rate))
    anomaly_indices = set(random.sample(range(num_records), num_anomalies))

    for idx in anomaly_indices:
        values[idx] = random.choice([
            random.uniform(85.0, 115.0),
            random.uniform(-10.0, 10.0)
        ])

    return pl.DataFrame({
        "timestamp": timestamps,
        "device_id": device_ids,
        "temperature": values
    })
