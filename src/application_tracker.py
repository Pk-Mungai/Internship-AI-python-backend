
import json
from datetime import datetime, timezone
from pathlib import Path


APPLICATION_STATUSES = {
    "saved",
    "applied",
    "shortlisted",
    "rejected",
    "accepted",
}


class ApplicationTracker:
    def __init__(self, storage_path="data/applications.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.storage_path.exists():
            self._save([])

    def _load(self) -> list[dict]:
        try:
            with self.storage_path.open("r", encoding="utf-8") as file:
                applications = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError("Application storage contains invalid JSON.") from error

        if not isinstance(applications, list):
            raise ValueError("Application storage must contain a JSON list.")

        return applications

    def _save(self, applications: list[dict]) -> None:
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(applications, file, indent=4, ensure_ascii=False)

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _validate_status(status: str) -> None:
        if status not in APPLICATION_STATUSES:
            allowed = ", ".join(sorted(APPLICATION_STATUSES))
            raise ValueError(f"Invalid status. Allowed statuses: {allowed}")

    def add_application(
        self,
        internship_id: str,
        status: str = "saved",
        notes: str = "",
    ) -> dict:
        if not isinstance(internship_id, str) or not internship_id.strip():
            raise ValueError("internship_id cannot be empty.")

        if not isinstance(notes, str):
            raise TypeError("notes must be a string.")

        self._validate_status(status)

        applications = self._load()
        internship_id = internship_id.strip()

        if any(
            item.get("internship_id") == internship_id
            for item in applications
        ):
            raise ValueError(
                f"Application for internship '{internship_id}' already exists."
            )

        now = self._timestamp()

        application = {
            "internship_id": internship_id,
            "status": status,
            "notes": notes.strip(),
            "created_at": now,
            "updated_at": now,
        }

        applications.append(application)
        self._save(applications)

        return application

    def get_application(self, internship_id: str) -> dict | None:
        applications = self._load()

        for application in applications:
            if application.get("internship_id") == internship_id:
                return application

        return None

    def list_applications(
        self,
        status: str | None = None,
    ) -> list[dict]:
        applications = self._load()

        if status is not None:
            self._validate_status(status)
            applications = [
                item for item in applications
                if item.get("status") == status
            ]

        return applications

    def update_status(
        self,
        internship_id: str,
        status: str,
    ) -> dict:
        self._validate_status(status)
        applications = self._load()

        for application in applications:
            if application.get("internship_id") == internship_id:
                application["status"] = status
                application["updated_at"] = self._timestamp()
                self._save(applications)
                return application

        raise KeyError(
            f"No application found for internship '{internship_id}'."
        )

    def update_notes(
        self,
        internship_id: str,
        notes: str,
    ) -> dict:
        if not isinstance(notes, str):
            raise TypeError("notes must be a string.")

        applications = self._load()

        for application in applications:
            if application.get("internship_id") == internship_id:
                application["notes"] = notes.strip()
                application["updated_at"] = self._timestamp()
                self._save(applications)
                return application

        raise KeyError(
            f"No application found for internship '{internship_id}'."
        )

    def delete_application(self, internship_id: str) -> bool:
        applications = self._load()

        updated_applications = [
            item for item in applications
            if item.get("internship_id") != internship_id
        ]

        if len(updated_applications) == len(applications):
            return False

        self._save(updated_applications)
        return True
