"""
ACE-Omega Data Processor — Paper analysis, clustering, universe generation.
"""

import json, math, random, hashlib
from typing import List, Dict
from dataclasses import dataclass, field
import numpy as np
import pandas as pd


@dataclass
class Paper:
    id: str = ""
    title: str = ""
    authors: str = ""
    year: int = 2020
    cited_by_count: int = 0
    abstract: str = ""
    keywords: str = ""
    doi: str = ""
    module: str = "Other"
    journal: str = ""
    mass: float = 0.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    radius: float = 1.0
    color: str = "#888888"
    is_blackhole: bool = False
    is_dyson: bool = False
    pagerank: float = 0.0
    cluster: int = 0


MODULE_COLORS = {
    "ACN": "#00BFFF", "ASM": "#32CD32", "ACE": "#9370DB",
    "CROSS": "#FFA500", "Other": "#8ab4f8",
    # Extra mappings
    "CS": "#00BFFF", "AI": "#9370DB", "ML": "#32CD32",
    "NLP": "#FFA500", "BIO": "#81c995", "MED": "#f28b82",
    "PHY": "#c58af9", "MATH": "#fdd663", "ENG": "#ff8a65",
}


def generate_paper_id(title, year, doi):
    raw = f"{title}{year}{doi}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def df_to_papers(df: pd.DataFrame) -> List[Paper]:
    """Convert normalized DataFrame to Paper objects."""
    papers = []
    for _, row in df.iterrows():
        mod = str(row.get('module', 'Other')).upper().strip()
        if mod not in MODULE_COLORS:
            mod = "Other"
        p = Paper(
            title=str(row.get('title', 'Untitled')),
            authors=str(row.get('authors', 'Unknown')),
            year=int(row.get('year', 2020)),
            cited_by_count=int(row.get('cited_by_count', 0)),
            abstract=str(row.get('abstract', ''))[:500],
            keywords=str(row.get('keywords', '')),
            doi=str(row.get('doi', '')),
            module=mod,
            journal=str(row.get('journal', '')),
            color=MODULE_COLORS.get(mod, "#8ab4f8"),
        )
        p.id = generate_paper_id(p.title, p.year, p.doi)
        papers.append(p)
    return papers


def compute_properties(papers: List[Paper]) -> List[Paper]:
    """Compute mass, positions, radii, detect black holes / dyson spheres."""
    if not papers:
        return papers

    max_cited = max((p.cited_by_count for p in papers), default=1) or 1
    mean_cited = np.mean([p.cited_by_count for p in papers]) if papers else 1

    for p in papers:
        p.mass = 1.0 + math.log10(1 + p.cited_by_count + 1) * 2.5
        p.radius = 3.0 + math.log10(1 + p.cited_by_count + 1) * 2.5
        if mean_cited > 0 and p.cited_by_count > mean_cited * 50:
            p.is_blackhole = True

    sorted_p = sorted(papers, key=lambda x: x.cited_by_count, reverse=True)
    top_01 = max(1, int(len(papers) * 0.001))
    top_1 = max(1, int(len(papers) * 0.01))
    for i, p in enumerate(sorted_p):
        p.pagerank = 1.0 - (i / max(len(papers), 1))
        if i < top_01:
            p.is_blackhole = True
        if i < top_1 and p.cited_by_count > mean_cited * 10:
            p.is_dyson = True

    years = [p.year for p in papers]
    min_y, max_y = min(years), max(years)
    span = max(max_y - min_y, 1)

    # Assign module z-offsets dynamically
    unique_mods = list(set(p.module for p in papers))
    mod_z = {m: (i - len(unique_mods)/2) * 12 for i, m in enumerate(unique_mods)}

    for p in papers:
        t = (p.year - min_y) / span
        p.x = (t - 0.5) * 80 + random.gauss(0, 2)
        p.y = math.log10(1 + p.cited_by_count) * 15 + random.gauss(0, 1.5)
        p.z = mod_z.get(p.module, 0) + random.gauss(0, 4)

    return papers


def generate_demo(n: int = 120) -> List[Paper]:
    """Generate realistic demo dataset."""
    topics = {
        "ACN": ["Deep Learning for Citation Networks", "Graph Neural Networks for Scholarly Knowledge",
                "Citation Pattern Analysis", "Academic Co-authorship Dynamics",
                "Multi-modal Entity Resolution", "Heterogeneous Network Embedding",
                "Citation Graph Evolution", "Influence Propagation Modeling"],
        "ASM": ["Assembly Optimization Techniques", "Binary Analysis with ML",
                "Reverse Engineering Automation", "Firmware Vulnerability Detection",
                "RISC-V Verification", "Compiler Backend Optimization",
                "Side Channel Analysis", "ISA Evolution"],
        "ACE": ["Knowledge Universe Visualization", "Interactive Scholarly Exploration",
                "AI-Powered Literature Review", "Research Gap Detection via NLP",
                "Automated Systematic Review", "Academic Trend Forecasting",
                "Bibliometric Dashboard", "Meta-research Framework"],
        "CROSS": ["Bridging NLP and Network Science", "Cross-disciplinary Innovation",
                  "Interdisciplinary Impact Metrics", "Knowledge Convergence"],
    }
    authors_pool = [
        "Zhang W., Li H.", "Smith J., Johnson A.", "Chen X., Wang Y.",
        "Kim S., Park J.", "Mueller K., Schmidt T.", "Patel R., Kumar S.",
        "Garcia M., Lopez F.", "Tanaka H., Suzuki K.", "Brown D., Wilson E.",
    ]
    papers = []
    for i in range(n):
        mod = random.choices(["ACN", "ASM", "ACE", "CROSS"], weights=[35, 25, 30, 10])[0]
        title = random.choice(topics[mod])
        year = random.randint(2015, 2025)
        cited = int(np.random.pareto(1.2) * 15)
        if i < 3: cited = random.randint(500, 2000)
        elif i < 10: cited = random.randint(100, 500)
        kws = ", ".join(random.sample(["deep learning", "GNN", "citation", "NLP",
            "knowledge graph", "visualization", "transformer", "benchmark",
            "survey", "optimization", "scalability", "interactive"], 4))
        p = Paper(title=title, authors=random.choice(authors_pool), year=year,
                  cited_by_count=cited, abstract=f"Research on {title.lower()} with novel approaches.",
                  keywords=kws, doi=f"10.1000/ace.{year}.{i:04d}", module=mod,
                  color=MODULE_COLORS.get(mod, "#8ab4f8"))
        p.id = generate_paper_id(p.title, p.year, p.doi)
        papers.append(p)
    return compute_properties(papers)


def papers_to_json(papers: List[Paper]) -> str:
    return json.dumps([{
        "id": p.id, "title": p.title, "authors": p.authors, "year": p.year,
        "cited": p.cited_by_count, "abstract": p.abstract[:120],
        "keywords": p.keywords, "doi": p.doi, "module": p.module,
        "mass": round(p.mass, 3), "x": round(p.x, 2), "y": round(p.y, 2),
        "z": round(p.z, 2), "radius": round(p.radius, 2), "color": p.color,
        "isBlackhole": p.is_blackhole, "isDyson": p.is_dyson,
        "pagerank": round(p.pagerank, 4), "cluster": p.cluster,
    } for p in papers], ensure_ascii=False)


def compute_stats(papers: List[Paper]) -> dict:
    if not papers:
        return {}
    cites = [p.cited_by_count for p in papers]
    years = [p.year for p in papers]
    mods = {}
    for p in papers:
        mods[p.module] = mods.get(p.module, 0) + 1
    return {
        "total_papers": len(papers), "total_citations": sum(cites),
        "mean_citations": round(np.mean(cites), 1), "max_citations": max(cites),
        "year_min": min(years), "year_max": max(years), "modules": mods,
        "blackholes": sum(1 for p in papers if p.is_blackhole),
        "dyson_spheres": sum(1 for p in papers if p.is_dyson),
        "top_5": sorted(papers, key=lambda x: x.cited_by_count, reverse=True)[:5],
    }
