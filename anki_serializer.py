from pathlib import Path

from vocabulary import VocabularyItem, VocabularyList

cache_dir = Path(".cache")


def serialize_anki(vocab_list: VocabularyList, output_path: Path) -> None:
    """Create Anki deck format from vocabulary list."""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("#notetype:Basic (and reversed card)\n")
        f.write("#deck:vhs-learn A1\n")
        f.write("#separator:tab\n")
        f.write("#html:false\n")
        f.write("#tags column:3\n")
        for item in vocab_list.items:
            f.write(f"{item.word}\t{item.translation}\t{item.tags}\n")


def deserialize_anki(input_path: Path) -> VocabularyList:
    """Deserialize Anki deck format to vocabulary list."""
    items = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                word, translation = parts[0], parts[1]
                tags = parts[2] if len(parts) > 2 else ""
                items.append(
                    VocabularyItem(word=word, translation=translation, tags=tags)
                )
    return VocabularyList(items=items)
