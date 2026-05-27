"""Basic repository self-check for ACE-Omega Academic Universe."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "app.py",
    "requirements.txt",
    "README.md",
    "utils/data_processor.py",
    "utils/file_parser.py",
    "utils/ace_model.py",
    "utils/components.py",
    "pages/01_Universe_Overview.py",
]

for item in REQUIRED:
    path = ROOT / item
    if not path.exists():
        raise SystemExit(f"Missing required file: {item}")

for path in list((ROOT / "utils").glob("*.py")) + [ROOT / "app.py"] + list((ROOT / "pages").glob("*.py")):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

print("ACE-Omega selfcheck passed.")
