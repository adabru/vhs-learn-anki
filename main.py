import time
from pathlib import Path

import requests

from anki_serializer import deserialize_anki, serialize_anki
from vhs_learn_serializer import deserialize_vhs_learn
from vocabulary import Locale, VocabularyItem, VocabularyTable


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


def add_missing_translations(
    vocab_list: VocabularyTable, target_languages: list[Locale]
) -> None:
    """Translate vocabulary items using a translation API."""
    untranslated_count = 0
    for run_id in ["count", "translate"]:
        i = 0
        for target_locale in target_languages:
            target_lang = target_locale.code
            for idx, translations in vocab_list.entries.items():
                item = translations.get(Locale(code="de"))
                assert item is not None, f"Missing German translation for entry {idx}"
                if target_locale not in translations:
                    i += 1
                    if run_id == "translate":
                        print(
                            f"Translating {i}/{untranslated_count} '{item.text}' to {target_lang}..."
                        )
                        translation = google_translate(
                            item.text, source_lang="de", target_lang=target_lang
                        )
                        vocab_list.entries[idx][target_locale] = VocabularyItem(
                            text=translation, tags=item.tags
                        )
        untranslated_count = i


cache_dir = Path(".cache")
cards_dir = Path("cards")
cache_dir.mkdir(exist_ok=True)
target_languages = [Locale(code="ak"), Locale(code="en")]


def main():
    vocabulary_path = cache_dir / "vocab_list.json"
    card_files = list(cards_dir.glob("vhs-learn_A1_*.txt"))

    if len(card_files) > 0:
        vocabulary = VocabularyTable(entries={})
        # initialize vocabulary from existing/exported Anki decks if available
        for card_file in card_files:
            print(f"Loading existing Anki deck {card_file.name}...")
            deck_vocab = deserialize_anki(card_file)
            vocabulary.update(deck_vocab)
    elif vocabulary_path.exists():
        # otherwise, initialize vocabulary list from cached JSON file if available
        vocabulary = VocabularyTable.deserialize(vocabulary_path)
    else:
        # otherwise, initialize vocabulary list from vhs-learn.de portal
        vocabulary = deserialize_vhs_learn()
        vocabulary.serialize(vocabulary_path)

    # add missing translations using Google Translate API
    add_missing_translations(vocabulary, target_languages)

    # update Anki decks with new translations
    for target_locale in target_languages:
        card_file = cards_dir / f"vhs-learn_A1_{target_locale.code}.txt"
        serialize_anki(vocabulary, target_locale, card_file)

    print("Done!")


if __name__ == "__main__":
    main()
