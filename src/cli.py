import time
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import polars as pl

from src.generator import generate_telemetry
from src.detector import detect_anomalies_zscore

app = typer.Typer(
    name="logpulse",
    help="LogPulse: CLI Tabanlı Telemetri & Anomali Tespit Motoru",
    add_completion=False
)
console = Console()

@app.command()
def generate(
    records: int = typer.Option(15000, "--records", "-n", help="Üretilecek kayıt sayısı"),
    anomaly_rate: float = typer.Option(0.02, "--rate", "-r", help="Aykırı değer oranı"),
    output: str = typer.Option("telemetry.csv", "--output", "-o", help="Kayıt edilecek CSV dosya adı")
):
    start_time = time.perf_counter()
    with console.status("[bold green]Veri üretiliyor...[/bold green]"):
        df = generate_telemetry(num_records=records, anomaly_rate=anomaly_rate)
        df.write_csv(output)
    
    elapsed = time.perf_counter() - start_time
    console.print(
        f"[bold green]✔ Başarılı:[/bold green] [cyan]{records:,}[/cyan] satır "
        f"[yellow]{output}[/yellow] dosyasına yazıldı ({elapsed:.2f} sn)."
    )

@app.command()
def scan(
    file_path: str = typer.Argument(..., help="Taranacak CSV dosya yolu"),
    column: str = typer.Option("temperature", "--column", "-c", help="Analiz edilecek sütun"),
    threshold: float = typer.Option(3.0, "--threshold", "-t", help="Z-score eşik değeri"),
    top: int = typer.Option(10, "--top", help="Gösterilecek maksimum anomali sayısı")
):
    target_path = Path(file_path)
    if not target_path.exists():
        console.print(f"[bold red]Hata:[/bold red] '{file_path}' dosyası bulunamadı.")
        raise typer.Exit(code=1)

    start_time = time.perf_counter()
    df = pl.read_csv(file_path)
    
    try:
        _, anomalies = detect_anomalies_zscore(df, metric_col=column, threshold=threshold)
    except Exception as e:
        console.print(f"[bold red]Hata:[/bold red] {e}")
        raise typer.Exit(code=1)

    elapsed = time.perf_counter() - start_time
    total_rows = len(df)
    anomaly_count = len(anomalies)
    ratio = (anomaly_count / total_rows) * 100 if total_rows > 0 else 0

    summary_text = (
        f"[bold]Dosya:[/bold] {file_path}\n"
        f"[bold]Toplam Satır:[/bold] {total_rows:,}\n"
        f"[bold]Hedef Sütun:[/bold] {column}\n"
        f"[bold]Eşik (Z-Score):[/bold] {threshold}\n"
        f"[bold]Tespit Edilen Anomali:[/bold] [bold red]{anomaly_count}[/bold red] (%{ratio:.2f})\n"
        f"[bold]Tarama Süresi:[/bold] {elapsed:.3f} saniye"
    )
    console.print(Panel(summary_text, title="[bold cyan]Tarama Özeti[/bold cyan]", expand=False))

    if anomaly_count > 0:
        table = Table(
            title=f"En Belirgin İlk {min(top, anomaly_count)} Anomali",
            header_style="bold magenta",
            show_lines=False
        )
        table.add_column("Zaman Damgası", style="dim")
        table.add_column("Cihaz ID", style="cyan")
        table.add_column(f"{column} Değeri", justify="right")
        table.add_column("Z-Score", justify="right", style="bold red")

        sorted_anomalies = anomalies.sort("z_score", descending=True).head(top)

        for row in sorted_anomalies.iter_rows(named=True):
            table.add_row(
                str(row.get("timestamp", "-")),
                str(row.get("device_id", "-")),
                f"{row[column]:.2f}",
                f"{row['z_score']:.2f}"
            )
        console.print(table)
    else:
        console.print("[bold green]Tebrikler! Belirlenen eşik değerini aşan anomali bulunamadı.[/bold green]")
