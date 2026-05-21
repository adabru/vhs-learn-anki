import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class Locale:
    # 2-letter ISO 639-1 language code
    code: str


@dataclass(frozen=True)
class VocabularyItem:
    tags: str
    text: str


@dataclass
class VocabularyTable:
    entries: Dict[int, Dict[Locale, VocabularyItem]]

    def serialize(self, output_path: Path) -> None:
        """Serialize vocabulary list to JSON."""
        serializable_entries = {
            k: {str(lk.code): asdict(lv) for lk, lv in v.items()}
            for k, v in self.entries.items()
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                serializable_entries, f, ensure_ascii=False, indent=2, default=str
            )

    @staticmethod
    def deserialize(input_path: Path) -> "VocabularyTable":
        """Deserialize vocabulary list from JSON."""
        with open(input_path, "r", encoding="utf-8") as f:
            vocab_raw = json.load(f)
            return VocabularyTable(
                entries={
                    int(k): {
                        Locale(code=lk): VocabularyItem(**lv) for lk, lv in v.items()
                    }
                    for k, v in vocab_raw.items()
                }
            )

    def update(self, other: "VocabularyTable") -> None:
        """Update current vocabulary table with entries from another table."""
        for idx, translations in other.entries.items():
            if idx not in self.entries:
                self.entries[idx] = translations
            else:
                for locale, item in translations.items():
                    if locale not in self.entries[idx]:
                        self.entries[idx][locale] = item
                    else:
                        self.entries[idx][locale] = item
