import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

import pdfplumber
import requests


@dataclass
class VocabularyItem:
    tags: str
    word: str
    translation: str | None


@dataclass
class VocabularyList:
    items: List[VocabularyItem]


def google_translate(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text using the public Google Translate endpoint."""
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": source_lang,
        "tl": target_lang,
        "dt": "t",
        "q": text,
    }

    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            translated_chunks = [chunk[0] for chunk in data[0] if chunk and chunk[0]]
            if translated_chunks:
                return "".join(translated_chunks).strip()
        except (
            requests.RequestException,
            ValueError,
            IndexError,
            TypeError,
        ) as err:
            if attempt == 2:
                print(f"Translation failed for '{text}': {err}")
                return text
            time.sleep(1)

    return text


def download_pdf(output_path: Path) -> None:
    """Download PDF from URL and save locally."""
    url = "https://www.vhs-lernportal.de/wws/bin/4007498-4014834-1-dvv_wortschatzlisten_a1.pdf"
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)


def extract_tables_from_pdf(pdf_path: Path, output_path: Path) -> None:
    """Extract table from PDF and convert to list of dicts."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"Extracting tables from page {i + 1}/{len(pdf.pages)}...")
            page_tables = page.extract_tables()
            tables.extend(page_tables)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tables, f, ensure_ascii=False, indent=2)


def generate_vocab_list_from_tables(
    tables: List[List[List[str]]], output_path: Path
) -> None:
    """Convert extracted tables to a list of vocabulary items."""
    vocab = VocabularyList(items=[])
    for table in tables:
        # skip lecture name and empty row
        header = table[0][0].replace(" ", "").strip()
        for row in table[2:]:
            vocab.items.append(
                VocabularyItem(word=row[0], translation=None, tags=f"A1 {header}")
            )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asdict(vocab), f, ensure_ascii=False, indent=2)


def translate_vocab_list(vocab_list: VocabularyList, output_path: Path) -> None:
    """Translate vocabulary items using a translation API."""
    source_lang = "de"
    target_lang = "ak"  # Twi is covered under Akan in Google Translate.

    untranslated_list = [item for item in vocab_list.items if item.translation is None]
    for i, item in enumerate(untranslated_list):
        if item.translation is None:
            print(f"Translating {i + 1}/{len(untranslated_list)} '{item.word}'...")
            item.translation = google_translate(item.word, source_lang, target_lang)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asdict(vocab_list), f, ensure_ascii=False, indent=2)


def create_anki_deck(vocab_list: VocabularyList, output_path: Path) -> None:
    """Create Anki deck format from vocabulary list."""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("#notetype:Basic (and reversed card)\n")
        f.write("#deck:vhs-learn A1\n")
        f.write("#separator:tab\n")
        f.write("#html:false\n")
        f.write("#tags column:3\n")
        for item in vocab_list.items:
            f.write(f"{item.word}\t{item.translation}\t{item.tags}\n")


def main():
    Path(".cache").mkdir(exist_ok=True)

    pdf_path = Path(".cache/vocab.pdf")
    extracted_tables_path = Path(".cache/extracted_data.json")
    vocab_list_path = Path(".cache/vocab_list.json")
    anki_deck_path = Path(".cache/vhs_learn_A1.txt")

    if not pdf_path.exists():
        print("Downloading PDF...")
        download_pdf(pdf_path)

    if not extracted_tables_path.exists():
        print("Extracting table from PDF...")
        extract_tables_from_pdf(pdf_path, extracted_tables_path)

    with open(extracted_tables_path, "r", encoding="utf-8") as f:
        extracted_tables = json.load(f)

    if not vocab_list_path.exists():
        print("Extracting vocabulary list from tables...")
        generate_vocab_list_from_tables(extracted_tables, vocab_list_path)

    with open(vocab_list_path, "r", encoding="utf-8") as f:
        vocab_raw = json.load(f)
        vocab_list = VocabularyList(
            items=[VocabularyItem(**item) for item in vocab_raw["items"]]
        )

    if any(item.translation is None for item in vocab_list.items):
        translate_vocab_list(vocab_list, vocab_list_path)

    if not anki_deck_path.exists():
        print("Creating Anki deck...")
        create_anki_deck(vocab_list, anki_deck_path)

    print("Done!")


if __name__ == "__main__":
    main()
