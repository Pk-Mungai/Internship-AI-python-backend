
import json
from pathlib import Path

from pydantic import ValidationError

from src.internship_model import Internship


class InternshipRepository:
    """JSON-based storage for internship records."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def load_all(self) -> list[Internship]:
        if not self.file_path.exists():
            return []

        try:
            data = json.loads(
                self.file_path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                "Internship database contains invalid JSON."
            ) from error

        if not isinstance(data, list):
            raise ValueError(
                "Internship database must contain a JSON list."
            )

        try:
            internships = [
                Internship.model_validate(item)
                for item in data
            ]
        except ValidationError:
            raise

        self._check_duplicate_ids(internships)
        return internships

    def get_by_id(self, internship_id: str) -> Internship | None:
        for internship in self.load_all():
            if internship.id == internship_id:
                return internship

        return None

    def save_all(self, internships: list[Internship]) -> None:
        self._check_duplicate_ids(internships)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = [
            internship.model_dump(mode="json")
            for internship in internships
        ]

        temporary_path = self.file_path.with_suffix(
            self.file_path.suffix + ".tmp"
        )

        temporary_path.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )

        temporary_path.replace(self.file_path)

    def upsert(self, internship: Internship) -> None:
        internships = self.load_all()

        for index, existing in enumerate(internships):
            if existing.id == internship.id:
                internships[index] = internship
                self.save_all(internships)
                return

        internships.append(internship)
        self.save_all(internships)

    @staticmethod
    def _check_duplicate_ids(
        internships: list[Internship]
    ) -> None:
        ids = [internship.id for internship in internships]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "Internship IDs must be unique."
            )
