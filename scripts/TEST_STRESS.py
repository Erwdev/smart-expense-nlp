"""
Comprehensive Stress Testing & Profiling Suite
Run: python TEST_STRESS.py
"""
import requests
import json
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich import box
    from rich.live import Live
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'rich', '--quiet'])
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich import box
    from rich.live import Live

console = Console()

BASE_URL = "http://localhost:8000"

# Test data
TEST_CASES = [
    "beli pulsa 25k",
    "grab food 60rb",
    "parkir 10k",
    "bayar kontrakan 3.8jt",
    "3x kopi hitam @ 25k",
    "ongkir shopee 28k",
    "bensin pertalite 50rb",
    "bayar listrik 450rb",
    "beli beras 5kg 75k",
    "laundry 2 kilo 20rb",
]

class StressTestRunner:
    """
    Comprehensive stress testing runner
    """
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = {
            "requests": [],
            "errors": [],
            "latencies": [],
            "throughput": []
        }
    
    def single_request(self, text: str) -> Dict[str, Any]:
        """Execute single API request"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/parse",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            latency = time.time() - start_time
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "latency": latency,
                "text": text,
                "response": response.json() if response.status_code == 200 else None,
                "error": None
            }
        except Exception as e:
            latency = time.time() - start_time
            return {
                "success": False,
                "status_code": 0,
                "latency": latency,
                "text": text,
                "response": None,
                "error": str(e)
            }
    
    def concurrent_load_test(self, num_requests: int, num_workers: int) -> List[Dict]:
        """
        Execute concurrent load test
        
        Args:
            num_requests: Total number of requests
            num_workers: Number of concurrent workers
        """
        results = []
        
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                f"[cyan]Load Test ({num_workers} workers)...",
                total=num_requests
            )
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = []
                
                for i in range(num_requests):
                    text = TEST_CASES[i % len(TEST_CASES)]
                    future = executor.submit(self.single_request, text)
                    futures.append(future)
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    progress.update(task, advance=1)
        
        return results
    
    def sustained_load_test(self, duration_seconds: int, requests_per_second: int) -> List[Dict]:
        """
        Sustained load test over time
        
        Args:
            duration_seconds: Test duration
            requests_per_second: Target RPS
        """
        results = []
        start_time = time.time()
        request_interval = 1.0 / requests_per_second
        
        console.print(f"\n[yellow]Sustained Load Test:[/yellow] {requests_per_second} RPS for {duration_seconds}s")
        
        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Running...", total=duration_seconds)
            
            while time.time() - start_time < duration_seconds:
                iteration_start = time.time()
                
                text = TEST_CASES[len(results) % len(TEST_CASES)]
                result = self.single_request(text)
                results.append(result)
                
                # Maintain RPS
                elapsed = time.time() - iteration_start
                if elapsed < request_interval:
                    time.sleep(request_interval - elapsed)
                
                progress.update(task, completed=int(time.time() - start_time))
        
        return results
    
    def spike_test(self, normal_rps: int, spike_rps: int, spike_duration: int = 10) -> List[Dict]:
        """
        Test with sudden traffic spike
        
        Args:
            normal_rps: Normal requests per second
            spike_rps: Spike requests per second
            spike_duration: Spike duration in seconds
        """
        console.print(f"\n[yellow]Spike Test:[/yellow] {normal_rps} RPS → {spike_rps} RPS for {spike_duration}s")
        
        results = []
        
        # Normal load (10s)
        console.print("[dim]Phase 1: Normal load (10s)[/dim]")
        results.extend(self.sustained_load_test(10, normal_rps))
        
        # Spike (spike_duration)
        console.print(f"[red]Phase 2: SPIKE ({spike_duration}s)[/red]")
        results.extend(self.sustained_load_test(spike_duration, spike_rps))
        
        # Recovery (10s)
        console.print("[dim]Phase 3: Recovery (10s)[/dim]")
        results.extend(self.sustained_load_test(10, normal_rps))
        
        return results
    
    def analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze test results"""
        if not results:
            return {}
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        latencies = [r["latency"] * 1000 for r in successful]  # Convert to ms
        
        # Calculate percentiles
        sorted_latencies = sorted(latencies) if latencies else [0]
        p50 = sorted_latencies[int(len(sorted_latencies) * 0.50)] if latencies else 0
        p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)] if latencies else 0
        p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)] if latencies else 0
        
        # Throughput
        if results:
            total_time = max([r["latency"] for r in results])
            throughput = len(successful) / total_time if total_time > 0 else 0
        else:
            throughput = 0
        
        return {
            "total_requests": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "latency_ms": {
                "min": min(latencies) if latencies else 0,
                "max": max(latencies) if latencies else 0,
                "mean": statistics.mean(latencies) if latencies else 0,
                "median": statistics.median(latencies) if latencies else 0,
                "p50": p50,
                "p95": p95,
                "p99": p99,
                "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0
            },
            "throughput_rps": throughput,
            "errors": [{"text": r["text"], "error": r["error"]} for r in failed]
        }

def create_results_table(analysis: Dict[str, Any]) -> Table:
    """Create results summary table"""
    table = Table(title="📊 Stress Test Results", box=box.DOUBLE_EDGE)
    
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Value", style="yellow", width=20)
    
    # Request stats
    table.add_row("Total Requests", str(analysis["total_requests"]))
    table.add_row("Successful", f"{analysis['successful']} ({analysis['success_rate']:.2f}%)", style="green")
    table.add_row("Failed", str(analysis["failed"]), style="red" if analysis["failed"] > 0 else "dim")
    
    table.add_row("", "")  # Separator
    
    # Latency stats
    lat = analysis["latency_ms"]
    table.add_row("[bold]Latency (ms)[/bold]", "")
    table.add_row("  ├─ Min", f"{lat['min']:.2f}")
    table.add_row("  ├─ Mean", f"{lat['mean']:.2f}")
    table.add_row("  ├─ Median", f"{lat['median']:.2f}")
    table.add_row("  ├─ P95", f"{lat['p95']:.2f}", style="yellow")
    table.add_row("  ├─ P99", f"{lat['p99']:.2f}", style="red")
    table.add_row("  └─ Max", f"{lat['max']:.2f}")
    
    table.add_row("", "")
    table.add_row("Throughput", f"{analysis['throughput_rps']:.2f} req/s", style="green")
    
    return table

def main():
    """Main stress test execution"""
    console.clear()
    
    # Header
    console.print(Panel.fit(
        "[bold cyan]Smart Expense NER API - Stress Test Suite[/bold cyan]\n"
        f"[dim]Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="cyan"
    ))
    
    runner = StressTestRunner(BASE_URL)
    
    # Test 1: Concurrent Load Test
    console.print("\n[bold yellow]═══ Test 1: Concurrent Load (100 requests, 10 workers) ═══[/bold yellow]")
    results1 = runner.concurrent_load_test(num_requests=100, num_workers=10)
    analysis1 = runner.analyze_results(results1)
    console.print(create_results_table(analysis1))
    
    # Test 2: High Concurrency
    console.print("\n[bold yellow]═══ Test 2: High Concurrency (200 requests, 50 workers) ═══[/bold yellow]")
    results2 = runner.concurrent_load_test(num_requests=200, num_workers=50)
    analysis2 = runner.analyze_results(results2)
    console.print(create_results_table(analysis2))
    
    # Test 3: Sustained Load
    console.print("\n[bold yellow]═══ Test 3: Sustained Load (30s, 10 RPS) ═══[/bold yellow]")
    results3 = runner.sustained_load_test(duration_seconds=30, requests_per_second=10)
    analysis3 = runner.analyze_results(results3)
    console.print(create_results_table(analysis3))
    
    # Test 4: Spike Test
    console.print("\n[bold yellow]═══ Test 4: Spike Test (5 RPS → 50 RPS) ═══[/bold yellow]")
    results4 = runner.spike_test(normal_rps=5, spike_rps=50, spike_duration=10)
    analysis4 = runner.analyze_results(results4)
    console.print(create_results_table(analysis4))
    
    # Export results
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "tests": {
            "concurrent_load_10w": analysis1,
            "high_concurrency_50w": analysis2,
            "sustained_load_30s": analysis3,
            "spike_test": analysis4
        }
    }
    
    filename = f"stress_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    console.print(f"\n[green]✓ Results exported to: {filename}[/green]")
    
    # Final summary
    console.print(Panel.fit(
        "[bold green]All Stress Tests Complete![/bold green]\n"
        f"Total Requests Across All Tests: {sum([len(r) for r in [results1, results2, results3, results4]])}",
        border_style="green"
    ))

if __name__ == "__main__":
    main()