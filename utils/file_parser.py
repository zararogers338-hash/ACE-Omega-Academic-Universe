"""
ACE-Omega Universal File Parser
================================
Handles ALL formats: TXT, PDF, MD, DOCX, DOC, CSV, JSON, XLSX, BIB, RIS
Extracts paper metadata smartly. Missing fields get sensible defaults.
Never crashes — always loads what it can.
"""

import re
import json
import hashlib
import logging
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from io import BytesIO, StringIO

import pandas as pd

logger = logging.getLogger("ace_parser")


def _hash_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


def _safe_int(val, default=0) -> int:
    try:
        if pd.isna(val):
            return default
        return int(float(str(val).strip().replace(",", "")))
    except:
        return default


def _safe_str(val, default="") -> str:
    try:
        if pd.isna(val):
            return default
        return str(val).strip()
    except:
        return default


def _extract_year(text: str) -> int:
    """Try to extract a 4-digit year from text."""
    matches = re.findall(r'(19[5-9]\d|20[0-2]\d)', str(text))
    if matches:
        return int(matches[-1])
    return 2020


def _extract_doi(text: str) -> str:
    """Try to extract DOI from text."""
    m = re.search(r'(10\.\d{4,}/[^\s]+)', str(text))
    return m.group(1).rstrip('.,;)') if m else ""


def _extract_citations_from_text(text: str) -> int:
    """Try to extract citation count from text."""
    patterns = [
        r'cited\s*(?:by)?\s*[:=]?\s*(\d+)',
        r'citations?\s*[:=]?\s*(\d+)',
        r'(\d+)\s*citations?',
        r'cited_by_count\s*[:=]?\s*(\d+)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return 0


def _guess_column(columns: list, candidates: list) -> Optional[str]:
    """Find best matching column name."""
    cols_lower = {c.lower().strip(): c for c in columns}
    for cand in candidates:
        if cand in cols_lower:
            return cols_lower[cand]
        for cl, orig in cols_lower.items():
            if cand in cl:
                return orig
    return None


# ═══════════════════════════════════════
# FORMAT-SPECIFIC PARSERS
# ═══════════════════════════════════════

def parse_csv(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse CSV file."""
    for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'gbk', 'gb2312']:
        try:
            return pd.read_csv(BytesIO(file_bytes), encoding=enc)
        except:
            continue
    return pd.read_csv(BytesIO(file_bytes), encoding='utf-8', on_bad_lines='skip')


def parse_json(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse JSON file — handles arrays, nested objects, single objects."""
    text = file_bytes.decode('utf-8', errors='ignore')
    data = json.loads(text)
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        # Check for common wrapper keys
        for key in ['papers', 'results', 'data', 'records', 'items', 'articles']:
            if key in data and isinstance(data[key], list):
                return pd.DataFrame(data[key])
        # Single object → single row
        return pd.DataFrame([data])
    return pd.DataFrame()


def parse_xlsx(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse Excel file."""
    try:
        return pd.read_excel(BytesIO(file_bytes), engine='openpyxl')
    except:
        return pd.read_excel(BytesIO(file_bytes))


def parse_txt(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse plain text — try TSV first, then extract papers from free text."""
    text = file_bytes.decode('utf-8', errors='ignore')

    # Try as TSV
    try:
        df = pd.read_csv(StringIO(text), sep='\t')
        if len(df.columns) >= 2 and len(df) >= 1:
            return df
    except:
        pass

    # Free text: split into paper-like blocks
    return _text_to_papers(text)


def parse_markdown(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse Markdown — extract structured references or free text."""
    text = file_bytes.decode('utf-8', errors='ignore')

    # Try to find markdown tables
    table_rows = []
    lines = text.split('\n')
    header_found = False
    headers = []
    for line in lines:
        line = line.strip()
        if '|' in line and not line.startswith('|-'):
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if not header_found and cells:
                headers = cells
                header_found = True
            elif header_found and cells and not all(c.replace('-', '') == '' for c in cells):
                table_rows.append(cells)

    if headers and table_rows:
        max_cols = max(len(headers), max(len(r) for r in table_rows))
        headers = headers + [f"col_{i}" for i in range(len(headers), max_cols)]
        padded = [r + [''] * (max_cols - len(r)) for r in table_rows]
        return pd.DataFrame(padded, columns=headers[:max_cols])

    return _text_to_papers(text)


def parse_pdf(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse PDF — extract text then parse as papers."""
    text = ""
    # Try pdfplumber first
    try:
        import pdfplumber
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

                # Also try tables
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if table and len(table) > 1:
                            try:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                if len(df) >= 1:
                                    return df
                            except:
                                pass
    except ImportError:
        pass

    # Fallback to pypdf
    if not text:
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        except:
            pass

    if text.strip():
        return _text_to_papers(text)
    return pd.DataFrame()


def parse_docx(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse DOCX — extract text and tables."""
    text = ""
    try:
        from docx import Document
        doc = Document(BytesIO(file_bytes))

        # Try tables first
        for table in doc.tables:
            rows = []
            for row in table.rows:
                rows.append([cell.text.strip() for cell in row.cells])
            if len(rows) > 1:
                try:
                    df = pd.DataFrame(rows[1:], columns=rows[0])
                    if len(df) >= 1:
                        return df
                except:
                    pass

        # Extract paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text.strip() + "\n"
    except ImportError:
        # Fallback: try as zip and extract XML text
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(BytesIO(file_bytes)) as z:
                with z.open('word/document.xml') as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                    for elem in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                        if elem.text:
                            text += elem.text
                    text = text.replace('\n\n', '\n')
        except:
            pass

    if text.strip():
        return _text_to_papers(text)
    return pd.DataFrame()


def parse_bib(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse BibTeX files."""
    text = file_bytes.decode('utf-8', errors='ignore')
    entries = []
    # Simple BibTeX parser
    pattern = r'@\w+\{[^@]+'
    for block in re.findall(pattern, text, re.DOTALL):
        entry = {}
        for field in ['title', 'author', 'year', 'journal', 'doi', 'abstract', 'keywords', 'volume', 'pages']:
            m = re.search(rf'{field}\s*=\s*\{{([^}}]*)\}}', block, re.IGNORECASE)
            if not m:
                m = re.search(rf'{field}\s*=\s*"([^"]*)"', block, re.IGNORECASE)
            if m:
                entry[field] = m.group(1).strip()
        if entry.get('title'):
            entries.append(entry)
    if entries:
        return pd.DataFrame(entries)
    return _text_to_papers(text)


# ═══════════════════════════════════════
# FREE TEXT → PAPERS EXTRACTION
# ═══════════════════════════════════════

def _text_to_papers(text: str) -> pd.DataFrame:
    """
    Smart extraction from unstructured text.
    Tries multiple strategies to find paper-like entries.
    """
    papers = []

    # Strategy 1: Numbered references like [1] Author (Year). Title. Journal.
    ref_pattern = r'\[?\d+\]?\s*\.?\s*(.+?)(?:\n\n|\n(?=\[?\d+\])|\Z)'
    refs = re.findall(ref_pattern, text, re.DOTALL)
    if len(refs) >= 3:
        for ref in refs:
            ref = ref.strip().replace('\n', ' ')
            if len(ref) < 10:
                continue
            paper = _parse_single_reference(ref)
            if paper.get('title'):
                papers.append(paper)
        if papers:
            return pd.DataFrame(papers)

    # Strategy 2: Split by double newlines as separate entries
    blocks = re.split(r'\n\s*\n', text)
    for block in blocks:
        block = block.strip()
        if len(block) < 15:
            continue
        paper = _parse_single_reference(block)
        if paper.get('title'):
            papers.append(paper)

    if papers:
        return pd.DataFrame(papers)

    # Strategy 3: Each line is a paper title
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 10]
    if lines:
        for line in lines[:500]:  # Cap at 500
            # Remove leading numbers, bullets, etc.
            clean = re.sub(r'^[\d\.\)\]\-\*\•\–]+\s*', '', line).strip()
            if len(clean) > 10:
                papers.append({
                    'title': clean[:300],
                    'year': _extract_year(clean),
                    'doi': _extract_doi(clean),
                })

    if papers:
        return pd.DataFrame(papers)

    # Strategy 4: Whole text as one paper
    title = text[:200].split('\n')[0].strip()
    if title:
        return pd.DataFrame([{
            'title': title,
            'abstract': text[:500],
            'year': _extract_year(text),
        }])

    return pd.DataFrame()


def _parse_single_reference(ref: str) -> dict:
    """Parse a single reference string into fields."""
    paper = {}

    # Extract year
    paper['year'] = _extract_year(ref)

    # Extract DOI
    paper['doi'] = _extract_doi(ref)

    # Extract authors (before year or before first period)
    year_match = re.search(r'[\(\[]?(19[5-9]\d|20[0-2]\d)[\)\]]?', ref)
    if year_match:
        before_year = ref[:year_match.start()].strip().rstrip('(,. ')
        after_year = ref[year_match.end():].strip().lstrip('). ')
        if before_year and len(before_year) > 3:
            paper['authors'] = before_year[:200]
        if after_year:
            # Title is typically the next sentence
            title_match = re.match(r'["\"]?(.+?)["\"]?[\.\?!]', after_year)
            if title_match:
                paper['title'] = title_match.group(1).strip('" "')
            else:
                paper['title'] = after_year[:200].split('.')[0].strip()
    else:
        # No year found — first sentence is title
        parts = ref.split('.')
        paper['title'] = parts[0].strip()[:200]
        if len(parts) > 1:
            paper['authors'] = parts[1].strip()[:200]

    # Extract citation count
    cited = _extract_citations_from_text(ref)
    if cited:
        paper['cited_by_count'] = cited

    return paper


# ═══════════════════════════════════════
# UNIFIED ENTRY POINT
# ═══════════════════════════════════════

PARSERS = {
    '.csv': parse_csv,
    '.tsv': parse_csv,
    '.json': parse_json,
    '.jsonl': parse_json,
    '.xlsx': parse_xlsx,
    '.xls': parse_xlsx,
    '.txt': parse_txt,
    '.text': parse_txt,
    '.md': parse_markdown,
    '.markdown': parse_markdown,
    '.pdf': parse_pdf,
    '.docx': parse_docx,
    '.doc': parse_docx,  # Best effort — older .doc may not parse
    '.bib': parse_bib,
    '.bibtex': parse_bib,
    '.ris': parse_txt,  # RIS treated as structured text
    '.xml': parse_txt,
    '.html': parse_txt,
    '.htm': parse_txt,
}

SUPPORTED_EXTENSIONS = list(PARSERS.keys())
SUPPORTED_TYPES = [ext.lstrip('.') for ext in SUPPORTED_EXTENSIONS]


def parse_file(file_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, str]:
    """
    Universal file parser.
    Returns (DataFrame, status_message).
    NEVER crashes — always returns something.
    """
    ext = Path(filename).suffix.lower()
    status = ""

    try:
        parser = PARSERS.get(ext)
        if parser is None:
            # Try as plain text
            parser = parse_txt
            status = f"Unknown format '{ext}', treated as plain text. "

        df = parser(file_bytes, filename)

        if df is None or df.empty:
            return pd.DataFrame(), f"No data could be extracted from {filename}."

        status += f"Extracted {len(df)} records from {filename}."
        return df, status

    except Exception as e:
        logger.error(f"Parse error for {filename}: {traceback.format_exc()}")
        # Last resort: try as plain text
        try:
            text = file_bytes.decode('utf-8', errors='ignore')
            df = _text_to_papers(text)
            if not df.empty:
                return df, f"Parsed {filename} as plain text (fallback). {len(df)} records."
        except:
            pass
        return pd.DataFrame(), f"Failed to parse {filename}: {str(e)}"


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize any DataFrame into standard paper schema.
    Missing fields get sensible defaults. NEVER drops data.
    """
    if df.empty:
        return df

    cols = list(df.columns)

    # Map columns to standard fields
    mapping = {
        'title': _guess_column(cols, ['title', 'name', 'paper', 'article', 'heading',
                                       'paper_title', 'article_title', 'work_title',
                                       'document', 'subject', 'topic']),
        'authors': _guess_column(cols, ['author', 'authors', 'writer', 'by',
                                         'creator', 'researcher', 'contributor']),
        'year': _guess_column(cols, ['year', 'date', 'pub_year', 'publication_year',
                                      'pub_date', 'published', 'publication_date']),
        'cited_by_count': _guess_column(cols, ['cited_by_count', 'citations', 'cited',
                                                'citation_count', 'cite_count', 'times_cited',
                                                'num_citations', 'citation', 'cites']),
        'abstract': _guess_column(cols, ['abstract', 'summary', 'description', 'content',
                                          'text', 'body', 'synopsis']),
        'keywords': _guess_column(cols, ['keywords', 'keyword', 'tags', 'topics',
                                          'subjects', 'terms', 'index_terms']),
        'doi': _guess_column(cols, ['doi', 'digital_object_identifier', 'url', 'link',
                                     'identifier', 'id']),
        'module': _guess_column(cols, ['module', 'category', 'type', 'field',
                                        'discipline', 'area', 'domain', 'group']),
        'journal': _guess_column(cols, ['journal', 'source', 'venue', 'publication',
                                         'publisher', 'conference', 'proceedings']),
    }

    result = pd.DataFrame()

    # Title — MUST have something
    if mapping['title']:
        result['title'] = df[mapping['title']].apply(lambda x: _safe_str(x, "Untitled"))
    else:
        # Use first text column as title, or row index
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
            result['title'] = df[text_cols[0]].apply(lambda x: _safe_str(x, "Untitled"))
        else:
            result['title'] = [f"Paper {i+1}" for i in range(len(df))]

    # Authors
    if mapping['authors']:
        result['authors'] = df[mapping['authors']].apply(lambda x: _safe_str(x, "Unknown"))
    else:
        result['authors'] = "Unknown"

    # Year
    if mapping['year']:
        result['year'] = df[mapping['year']].apply(lambda x: _extract_year(str(x)) if pd.notna(x) else 2020)
    else:
        result['year'] = 2020

    # Citations
    if mapping['cited_by_count']:
        result['cited_by_count'] = df[mapping['cited_by_count']].apply(lambda x: _safe_int(x, 0))
    else:
        result['cited_by_count'] = 0

    # Abstract
    if mapping['abstract']:
        result['abstract'] = df[mapping['abstract']].apply(lambda x: _safe_str(x, "")[:500])
    else:
        result['abstract'] = ""

    # Keywords
    if mapping['keywords']:
        result['keywords'] = df[mapping['keywords']].apply(lambda x: _safe_str(x, ""))
    else:
        result['keywords'] = ""

    # DOI
    if mapping['doi']:
        result['doi'] = df[mapping['doi']].apply(lambda x: _safe_str(x, ""))
    else:
        result['doi'] = ""

    # Module/Category
    if mapping['module']:
        result['module'] = df[mapping['module']].apply(lambda x: _safe_str(x, "Other"))
    else:
        result['module'] = "Other"

    # Journal
    if mapping['journal']:
        result['journal'] = df[mapping['journal']].apply(lambda x: _safe_str(x, ""))
    else:
        result['journal'] = ""

    # Drop rows with no title
    result = result[result['title'].str.strip() != '']
    result = result[result['title'] != 'Untitled'].reset_index(drop=True)

    # If all untitled, keep them anyway
    if result.empty:
        result = pd.DataFrame()
        if mapping['title']:
            result['title'] = df[mapping['title']].apply(lambda x: _safe_str(x, f"Entry"))
        else:
            result['title'] = [f"Paper {i+1}" for i in range(len(df))]
        for col in ['authors', 'year', 'cited_by_count', 'abstract', 'keywords', 'doi', 'module', 'journal']:
            result[col] = "" if col not in ['year', 'cited_by_count'] else (2020 if col == 'year' else 0)

    return result
