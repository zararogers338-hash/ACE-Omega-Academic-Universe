"""Smoke test for ACE-Omega core data pipeline."""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from utils.file_parser import parse_file, normalize_dataframe
from utils.data_processor import df_to_papers, compute_properties, compute_stats, generate_demo, papers_to_json

sample = ROOT / "examples" / "sample_literature.csv"
raw, status = parse_file(sample.read_bytes(), sample.name)
assert not raw.empty, status
norm = normalize_dataframe(raw)
assert {"title", "authors", "year", "cited_by_count"}.issubset(set(norm.columns))
papers = compute_properties(df_to_papers(norm))
assert len(papers) >= 3
stats = compute_stats(papers)
assert stats["total_papers"] == len(papers)
assert "modules" in stats
payload = papers_to_json(papers)
assert "title" in payload

demo = compute_properties(generate_demo(10))
assert len(demo) == 10
print("ACE-Omega smoke test passed.")
