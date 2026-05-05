"""Repository for spec sessions persistence."""

import json
from typing import Optional
from sqlalchemy.orm import Session

from app.infrastructure.persistence.models import SpecSessionModel


class SpecSessionRepository:
    def __init__(self, db: Session):
        self._db = db

    def save(self, session_id: str, user_id: str, rules_dicts: list, summary: dict) -> None:
        model = self._db.query(SpecSessionModel).filter(
            SpecSessionModel.session_id == session_id
        ).first()
        if model:
            model.rules_json = json.dumps(rules_dicts, ensure_ascii=False)
            model.summary_json = json.dumps(summary, ensure_ascii=False)
        else:
            model = SpecSessionModel(
                session_id=session_id,
                user_id=user_id,
                rules_json=json.dumps(rules_dicts, ensure_ascii=False),
                summary_json=json.dumps(summary, ensure_ascii=False),
            )
            self._db.add(model)
        self._db.commit()

    def find(self, session_id: str) -> Optional[dict]:
        model = self._db.query(SpecSessionModel).filter(
            SpecSessionModel.session_id == session_id
        ).first()
        if not model:
            return None
        return {
            "user_id": str(model.user_id),
            "rules_dicts": json.loads(model.rules_json),
            "summary": json.loads(model.summary_json),
        }

    def delete(self, session_id: str) -> None:
        self._db.query(SpecSessionModel).filter(
            SpecSessionModel.session_id == session_id
        ).delete()
        self._db.commit()
