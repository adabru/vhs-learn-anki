import json
from pathlib import Path
from typing import List

import pdfplumber
import requests

from vocabulary import VocabularyItem, VocabularyList

cache_dir = Path(".cache")


def _download_pdf(output_path: Path) -> None:
    """Download PDF from URL and save locally."""
    url = "https://www.vhs-lernportal.de/wws/bin/4007498-4014834-1-dvv_wortschatzlisten_a1.pdf"
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)


def _extract_tables_from_pdf(pdf_path: Path, output_path: Path) -> None:
    """Extract table from PDF and convert to list of dicts."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"Extracting tables from page {i + 1}/{len(pdf.pages)}...")
            page_tables = page.extract_tables()
            tables.extend(page_tables)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tables, f, ensure_ascii=False, indent=2)


def _generate_vocab_list_from_tables(tables: List[List[List[str]]]) -> VocabularyList:
    """Convert extracted tables to a list of vocabulary items."""
    vocab = VocabularyList(items=[])
    for table in tables:
        # skip lecture name and empty row
        header = table[0][0].replace(" ", "").strip()
        for row in table[2:]:
            vocab.items.append(
                VocabularyItem(word=row[0], translation=None, tags=f"A1 {header}")
            )
    return vocab


def deserialize_vhs_learn() -> VocabularyList:
    pdf_path = Path(".cache/vocab.pdf")
    extracted_tables_path = Path(".cache/extracted_data.json")

    if not pdf_path.exists():
        print("Downloading PDF...")
        _download_pdf(pdf_path)

    if not extracted_tables_path.exists():
        print("Extracting table from PDF...")
        _extract_tables_from_pdf(pdf_path, extracted_tables_path)

    with open(extracted_tables_path, "r", encoding="utf-8") as f:
        extracted_tables = json.load(f)

    vocab_list = _generate_vocab_list_from_tables(extracted_tables)
    return vocab_list
