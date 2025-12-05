
"""
Advanced API Test Script with Table Display
Run: python TEST_API_ADVANCED.py (while API is running)
"""
import requests
import json
from datetime import datetime

# Try to import rich for beautiful tables, fallback to tabulate
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
    from rich import box
    USE_RICH = True
except ImportError:
    print("Installing rich library for better display...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'rich', '--quiet'])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
    from rich import box
    USE_RICH = True

console = Console()

BASE_URL = "http://localhost:8000"

# ============================================
# 20 Test Cases
# ============================================
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
    "sate ayam 10 tusuk 45k",
    "nasi goreng 2 porsi 30rb",
    "bayar wifi indihome 350k",
    "top up gopay 100k",
    "bayar asuransi 500rb",
    "beli voucher game 50k",
    "makan warteg 15rb",
    "potong rambut 35k",
    "bayar BPJS 80rb",
    "beli obat apotek 125k"
]

def test_health_check():
    """Test health endpoint"""
    console.print("\n[bold cyan]Testing Health Endpoint...[/bold cyan]")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        if response.status_code == 200:
            console.print(Panel.fit(
                f"[green]✓ API is healthy[/green]\n"
                f"Status: {data['status']}\n"
                f"Model Loaded: {data['model_loaded']}\n"
                f"Uptime: {data.get('uptime_seconds', 0):.2f}s",
                title="Health Check",
                border_style="green"
            ))
            return True
        else:
            console.print("[red]✗ Health check failed[/red]")
            return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False

def parse_single_text(text):
    """Parse single text and return result"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/parse",
            json={"text": text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        console.print(f"[red]Error parsing '{text}': {e}[/red]")
        return None

def create_entity_table(text, entities):
    """Create a rich table for entities"""
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Entity", style="cyan", width=15)
    table.add_column("Type", style="green", width=12)
    table.add_column("Position", style="yellow", width=10)
    table.add_column("Confidence", style="blue", width=12)
    
    if not entities:
        table.add_row("[dim]No entities found[/dim]", "-", "-", "-")
    else:
        for ent in entities:
            confidence = f"{ent['score']*100:.1f}%"
            position = f"{ent['start']}-{ent['end']}"
            
            # Color coding by entity type
            entity_type = ent['entity_group']
            if entity_type == 'PRICE':
                type_display = f"[green]{entity_type}[/green]"
            elif entity_type == 'QTY':
                type_display = f"[yellow]{entity_type}[/yellow]"
            elif entity_type == 'ITEM':
                type_display = f"[blue]{entity_type}[/blue]"
            else:
                type_display = entity_type
            
            table.add_row(
                f"[bold]{ent['word']}[/bold]",
                type_display,
                position,
                confidence
            )
    
    return table

def create_summary_table(results):
    """Create summary table of all results"""
    table = Table(
        title="📊 Parsing Results Summary",
        show_header=True,
        header_style="bold cyan",
        box=box.DOUBLE_EDGE
    )
    
    table.add_column("No", style="dim", width=4)
    table.add_column("Input Text", style="white", width=35)
    table.add_column("Entities Found", style="green", width=15)
    table.add_column("Types", style="yellow", width=20)
    table.add_column("Status", style="cyan", width=10)
    
    for idx, result in enumerate(results, 1):
        if result['data']:
            entities = result['data']['entities']
            entity_count = len(entities)
            
            # Extract unique entity types
            entity_types = list(set([e['entity_group'] for e in entities]))
            types_str = ", ".join(entity_types) if entity_types else "-"
            
            # Format entities display
            entities_display = []
            for e in entities:
                entities_display.append(f"{e['word']} ({e['entity_group']})")
            
            entities_str = ", ".join(entities_display) if entities_display else "None"
            
            status = "[green]✓[/green]" if entity_count > 0 else "[yellow]○[/yellow]"
            
            table.add_row(
                str(idx),
                result['text'][:35],
                entities_str[:15] if entities_str != "None" else "[dim]None[/dim]",
                types_str,
                status
            )
        else:
            table.add_row(
                str(idx),
                result['text'][:35],
                "[red]Error[/red]",
                "-",
                "[red]✗[/red]"
            )
    
    return table

def create_detailed_table(results):
    """Create detailed table with all entity information"""
    table = Table(
        title="🔍 Detailed Entity Analysis",
        show_header=True,
        header_style="bold magenta",
        box=box.HEAVY_EDGE
    )
    
    table.add_column("Input", style="cyan", width=25)
    table.add_column("Entity", style="yellow", width=15)
    table.add_column("Type", style="green", width=10)
    table.add_column("Confidence", style="blue", width=12)
    table.add_column("Position", style="white", width=10)
    
    for result in results:
        if result['data'] and result['data']['entities']:
            text = result['text']
            for idx, ent in enumerate(result['data']['entities']):
                # Only show text on first entity of each input
                text_display = text if idx == 0 else ""
                
                table.add_row(
                    text_display,
                    f"[bold]{ent['word']}[/bold]",
                    ent['entity_group'],
                    f"{ent['score']*100:.2f}%",
                    f"{ent['start']}-{ent['end']}"
                )
            # Add separator
            if result != results[-1]:
                table.add_row("", "", "", "", "", style="dim")
    
    return table

def create_statistics_table(results):
    """Create statistics table"""
    # Calculate statistics
    total_texts = len(results)
    successful_parses = sum(1 for r in results if r['data'] and r['data']['entities'])
    total_entities = sum(len(r['data']['entities']) for r in results if r['data'])
    
    # Count entity types
    entity_type_counts = {}
    for result in results:
        if result['data']:
            for ent in result['data']['entities']:
                etype = ent['entity_group']
                entity_type_counts[etype] = entity_type_counts.get(etype, 0) + 1
    
    # Average confidence
    all_scores = []
    for result in results:
        if result['data']:
            all_scores.extend([e['score'] for e in result['data']['entities']])
    avg_confidence = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Create table
    table = Table(
        title="📈 Statistics",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED
    )
    
    table.add_column("Metric", style="yellow", width=30)
    table.add_column("Value", style="green", width=20)
    
    table.add_row("Total Texts Processed", str(total_texts))
    table.add_row("Successful Parses", f"{successful_parses} ({successful_parses/total_texts*100:.1f}%)")
    table.add_row("Total Entities Found", str(total_entities))
    table.add_row("Average Entities per Text", f"{total_entities/total_texts:.2f}")
    table.add_row("Average Confidence", f"{avg_confidence*100:.2f}%")
    
    # Add entity type breakdown
    table.add_row("", "", style="dim")
    table.add_row("[bold]Entity Type Breakdown:[/bold]", "", style="cyan")
    for etype, count in sorted(entity_type_counts.items(), key=lambda x: x[1], reverse=True):
        table.add_row(f"  └─ {etype}", str(count))
    
    return table

def main():
    """Main test function"""
    console.clear()
    
    # Header
    console.print(Panel.fit(
        "[bold cyan]Smart Expense NER API - Advanced Test Suite[/bold cyan]\n"
        f"[dim]Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n"
        f"[dim]Total Test Cases: {len(TEST_CASES)}[/dim]",
        border_style="cyan"
    ))
    
    # Health check
    if not test_health_check():
        console.print("\n[red]Cannot proceed without healthy API. Please start the server.[/red]")
        return
    
    # Run tests
    console.print(f"\n[bold yellow]Processing {len(TEST_CASES)} test cases...[/bold yellow]\n")
    
    results = []
    for text in track(TEST_CASES, description="Parsing texts..."):
        data = parse_single_text(text)
        results.append({
            'text': text,
            'data': data
        })
    
    # Display individual results (first 5 detailed)
    console.print("\n[bold cyan]═══ Sample Detailed Results (First 5) ═══[/bold cyan]\n")
    for idx, result in enumerate(results[:5], 1):
        console.print(f"\n[bold yellow]Test Case #{idx}:[/bold yellow] [white]{result['text']}[/white]")
        if result['data']:
            table = create_entity_table(result['text'], result['data']['entities'])
            console.print(table)
        else:
            console.print("[red]Failed to parse[/red]")
    
    # Summary table
    console.print("\n[bold cyan]═══ Complete Summary Table ═══[/bold cyan]\n")
    console.print(create_summary_table(results))
    
    # Detailed analysis
    console.print("\n[bold cyan]═══ Detailed Entity Analysis ═══[/bold cyan]\n")
    console.print(create_detailed_table(results))
    
    # Statistics
    console.print("\n[bold cyan]═══ Statistics ═══[/bold cyan]\n")
    console.print(create_statistics_table(results))
    
    # Export to JSON
    export_filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(export_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    console.print(f"\n[green]✓ Results exported to: {export_filename}[/green]")
    
    # Final summary panel
    successful = sum(1 for r in results if r['data'] and r['data']['entities'])
    console.print(Panel.fit(
        f"[bold green]Testing Complete![/bold green]\n"
        f"Processed: {len(results)} texts\n"
        f"Successful: {successful} ({successful/len(results)*100:.1f}%)\n"
        f"Total Entities: {sum(len(r['data']['entities']) for r in results if r['data'])}",
        title="Summary",
        border_style="green"
    ))

if __name__ == "__main__":
    main()