from pathlib import Path

from vocabulary import Locale, VocabularyItem, VocabularyTable

cache_dir = Path(".cache")


def serialize_anki(
    vocabulary: VocabularyTable, locale: Locale, output_path: Path
) -> None:
    """Create Anki deck format from vocabulary list."""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("#notetype:Basic (and reversed card)\n")
        f.write("#deck:vhs-learn A1\n")
        f.write("#separator:tab\n")
        f.write("#html:true\n")
        f.write("#tags column:3\n")
        for _, translations in vocabulary.entries.items():
            text_de = translations.get(Locale(code="de"))
            text_other = translations.get(locale)
            if text_de and text_other:
                f.write(f"{text_de.text}\t{text_other.text}\t{text_de.tags}\n")


def deserialize_anki(input_path: Path) -> VocabularyTable:
    """Deserialize Anki deck format to vocabulary list."""
    vocabulary = VocabularyTable(entries={})
    locale_other = Locale(code=input_path.stem.split("_")[-1])
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                text_de, text_other, tags = (
                    parts[0],
                    parts[1],
                    parts[2] if len(parts) > 2 else "",
                )
                vocabulary.entries[len(vocabulary.entries)] = {
                    Locale(code="de"): VocabularyItem(text=text_de, tags=tags),
                    locale_other: VocabularyItem(text=text_other, tags=tags),
                }
    return vocabulary
