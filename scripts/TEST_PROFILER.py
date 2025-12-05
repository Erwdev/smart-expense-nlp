"""
API Performance Profiling Script
Run: python TEST_PROFILER.py
"""
import requests
import time
import psutil
import json
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    from rich.panel import Panel
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'rich', '--quiet'])
    from rich.console import Console
    from rich.table import Table
    from rich import box
    from rich.panel import Panel

console = Console()

BASE_URL = "http://localhost:8000"

class APIProfiler:
    """Profile API performance metrics"""
    
    def __init__(self):
        self.metrics = []
        self.process = psutil.Process()
    
    def profile_request(self, text: str):
        """Profile a single request"""
        # Pre-request metrics
        cpu_before = self.process.cpu_percent()
        mem_before = self.process.memory_info().rss / 1024 / 1024
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/parse",
                json={"text": text},
                headers={"Content-Type": "application/json"}
            )
            
            latency = (time.time() - start_time) * 1000  # ms
            
            # Post-request metrics
            cpu_after = self.process.cpu_percent()
            mem_after = self.process.memory_info().rss / 1024 / 1024
            
            metric = {
                "text": text,
                "latency_ms": latency,
                "status_code": response.status_code,
                "cpu_delta": cpu_after - cpu_before,
                "memory_mb": mem_after,
                "memory_delta_mb": mem_after - mem_before,
                "entities_found": len(response.json()["entities"]) if response.status_code == 200 else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            self.metrics.append(metric)
            return metric
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return None
    
    def create_profile_table(self) -> Table:
        """Create profiling results table"""
        table = Table(title="⚡ API Performance Profile", box=box.ROUNDED)
        
        table.add_column("Text", style="cyan", width=25)
        table.add_column("Latency", style="yellow", width=12)
        table.add_column("Entities", style="green", width=10)
        table.add_column("CPU Δ", style="blue", width=10)
        table.add_column("Memory", style="magenta", width=12)
        
        for m in self.metrics:
            table.add_row(
                m["text"][:25],
                f"{m['latency_ms']:.2f}ms",
                str(m["entities_found"]),
                f"{m['cpu_delta']:.1f}%",
                f"{m['memory_mb']:.1f}MB"
            )
        
        return table

def main():
    """Main profiler execution"""
    console.clear()
    
    console.print(Panel.fit(
        "[bold cyan]API Performance Profiler[/bold cyan]\n"
        f"[dim]Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="cyan"
    ))
    
    test_cases = [
        "beli pulsa 25k",
        "grab food 60rb",
        "bayar kontrakan 3.8jt",
        "3x kopi hitam @ 25k",
        "bensin pertalite 50rb",
    ]
    
    profiler = APIProfiler()
    
    console.print("\n[yellow]Profiling API requests...[/yellow]\n")
    
    for text in test_cases:
        profiler.profile_request(text)
        time.sleep(0.5)
    
    console.print(profiler.create_profile_table())
    
    # Export
    filename = f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(profiler.metrics, f, indent=2)
    
    console.print(f"\n[green]✓ Profile saved to: {filename}[/green]")

if __name__ == "__main__":
    main()