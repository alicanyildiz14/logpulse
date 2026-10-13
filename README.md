# LogPulse

CLI-based telemetry log generator and real-time statistical anomaly detection engine built with Python, Polars, and Typer.

## Features
- High Performance: Uses Polars expressions for fast in-memory Z-Score calculations.
- Telemetry Generator: Generates synthetic device telemetry data with injected spikes.
- Terminal UI: Clean CLI outputs and tabular visualizations via Rich.

## Usage
- Generate Data: python main.py generate --records 25000 --output telemetry.csv
- Scan Anomalies: python main.py scan telemetry.csv --column temperature --threshold 3.0

## Running Tests
pytest tests/
