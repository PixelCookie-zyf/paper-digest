#!/usr/bin/env python3
"""Paper Digest — Search, screen, summarize, and generate per-paper MDX files."""

import argparse
import logging
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

from config import settings
from paper_search import ArxivProvider
from paper_fetch import fetch_paper_content
from llm_summary import summarize_paper, screen_paper
from mdx_writer import generate_single_mdx
from history import mark_processed, get_processed_ids, show_history

console = Console()


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Search papers, AI-screen for quality, summarize one-by-one, generate per-paper MDX.",
        usage='python main.py [OPTIONS] [QUERY]',
    )
    parser.add_argument("query", nargs="?", default=None,
                        help=f'Search keyword (default: "{settings.default_query}")')
    parser.add_argument("--query", "-q", dest="query_flag", default=None,
                        help="Search keyword (alternative)")
    parser.add_argument("--max-papers", "-n", type=int, default=None,
                        help=f"Max papers this run (default: {settings.max_papers})")
    parser.add_argument("--output-dir", "-o", default=None,
                        help=f"Output directory (default: {settings.output_dir})")
    parser.add_argument("--no-screen", action="store_true",
                        help="Skip AI screening")
    parser.add_argument("--start-date", default=None,
                        help=f"Search from date (default: {settings.search_start_date})")
    parser.add_argument("--pool-size", type=int, default=None,
                        help=f"Candidate pool size (default: {settings.search_pool_size})")
    parser.add_argument("--history", action="store_true",
                        help="Show history and exit")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose logging")

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.history:
        show_history()
        return

    query = args.query or args.query_flag or settings.default_query
    max_papers = args.max_papers or settings.max_papers
    output_dir = args.output_dir or settings.output_dir
    start_date = args.start_date or settings.search_start_date
    pool_size = args.pool_size or settings.search_pool_size

    if not settings.llm_api_key:
        console.print("[bold red]LLM_API_KEY is not set! Configure .env first.[/]")
        sys.exit(1)

    # ── Header ──
    console.print()
    console.print(Panel(
        f"[bold]Query:[/] {query}\n"
        f"[bold]From:[/]  {start_date}\n"
        f"[bold]Model:[/] {settings.llm_model}\n"
        f"[bold]Pool:[/]  {pool_size} candidates\n"
        f"[bold]Goal:[/]  {max_papers} papers",
        title="[bold cyan]Paper Digest[/]",
        border_style="cyan",
    ))
    console.print()

    # ── Step 1: Search ──
    with console.status("[bold green]Searching arXiv...[/]", spinner="dots"):
        provider = ArxivProvider()
        candidates = provider.search(query, max_results=pool_size, start_date=start_date)

    if not candidates:
        console.print("[bold red]No papers found.[/] Try a different query or date range.")
        sys.exit(1)

    console.print(f"  Found [bold]{len(candidates)}[/] candidates from arXiv")

    # ── Step 2: Deduplicate ──
    processed_ids = get_processed_ids()
    fresh = []
    for p in candidates:
        pid = p.url.rstrip("/").split("/")[-1]
        if "v" in pid:
            pid = pid.rsplit("v", 1)[0]
        if pid not in processed_ids:
            fresh.append(p)

    skipped = len(candidates) - len(fresh)
    if skipped:
        console.print(f"  Filtered [dim]{skipped} already processed[/] → [bold]{len(fresh)}[/] new papers")
    else:
        console.print(f"  All [bold]{len(fresh)}[/] are new")

    if not fresh:
        console.print("\n[yellow]All candidates already processed! Try --pool-size or --start-date.[/]\n")
        return

    # ── Step 3: Process papers one by one ──
    processed_count = 0
    generated_files = []

    for i, paper in enumerate(fresh):
        if processed_count >= max_papers:
            break

        console.print()
        console.rule(f"[bold]Paper {i+1}/{len(fresh)}[/]")
        console.print(f"  [bold]{paper.title}[/]")
        console.print(f"  [dim]{paper.published} · {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}[/]")
        console.print()

        # ── Screening ──
        if not args.no_screen:
            with console.status("  [yellow]AI screening...[/]", spinner="dots"):
                t0 = time.time()
                worth, reason = screen_paper(paper)
                elapsed = time.time() - t0

            if not worth:
                console.print(f"  [red]SKIP[/] ({elapsed:.1f}s) {reason}")
                continue
            console.print(f"  [green]PASS[/] ({elapsed:.1f}s) {reason}")
        else:
            console.print("  [dim]Screening disabled[/]")

        # ── Download PDF ──
        with console.status("  [blue]Downloading PDF...[/]", spinner="dots"):
            t0 = time.time()
            paper.full_text = fetch_paper_content(paper.pdf_url)
            elapsed = time.time() - t0

        if paper.full_text:
            chars = len(paper.full_text)
            console.print(f"  [green]PDF extracted[/] ({elapsed:.1f}s) {chars:,} chars")
        else:
            console.print(f"  [yellow]No full text[/] — will use abstract only")

        # ── Summarize ──
        with console.status(f"  [magenta]{settings.llm_model} is reading and writing summary...[/]", spinner="dots"):
            t0 = time.time()
            summary = summarize_paper(paper)
            elapsed = time.time() - t0

        console.print(f"  [green]Summary done[/] ({elapsed:.1f}s)")

        # ── Generate MDX ──
        mdx_path = generate_single_mdx(paper, summary, output_dir)
        mark_processed(paper.url, paper.title, query, mdx_path)
        generated_files.append(mdx_path)
        processed_count += 1

        console.print(f"  [bold green]Saved:[/] {mdx_path}")

    # ── Summary ──
    console.print()
    if generated_files:
        table = Table(title=f"Done — {processed_count} paper(s) processed", border_style="green")
        table.add_column("#", style="dim", width=3)
        table.add_column("File", style="cyan")
        for idx, f in enumerate(generated_files, 1):
            table.add_row(str(idx), f)
        console.print(table)
    else:
        console.print("[yellow]No papers processed this run.[/]")
    console.print()


if __name__ == "__main__":
    main()
