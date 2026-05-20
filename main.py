import json
import time
from dataclasses import asdict
from pathlib import Path

import requests

from anki_serializer import serialize_anki
from vhs_learn_serializer import deserialize_vhs_learn
from vocabulary import VocabularyList


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


cache_dir = Path(".cache")
cache_dir.mkdir(exist_ok=True)


def main():
    anki_deck_path = cache_dir / "vhs_learn_A1.txt"
    vocab_list_path = Path(".cache/vocab_list.json")

    if not vocab_list_path.exists():
        vocab_list = deserialize_vhs_learn()
        vocab_list.serialize(vocab_list_path)
    else:
        vocab_list = VocabularyList.deserialize(vocab_list_path)

    if any(item.translation is None for item in vocab_list.items):
        translate_vocab_list(vocab_list, vocab_list_path)

    if not anki_deck_path.exists():
        print("Creating Anki deck...")
        serialize_anki(vocab_list, anki_deck_path)

    print("Done!")


if __name__ == "__main__":
    main()
