import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List


@dataclass
class VocabularyItem:
    tags: str
    word: str
    translation: str | None


@dataclass
class VocabularyList:
    items: List[VocabularyItem]

    def serialize(self, output_path: Path) -> None:
        """Serialize vocabulary list to JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    @staticmethod
    def deserialize(input_path: Path) -> "VocabularyList":
        """Deserialize vocabulary list from JSON."""
        with open(input_path, "r", encoding="utf-8") as f:
            vocab_raw = json.load(f)
            return VocabularyList(
                items=[VocabularyItem(**item) for item in vocab_raw["items"]]
            )
