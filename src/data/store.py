"""SQLite-backed data store for core recruiter objects.

Purpose:
    Provide CRUD primitives for roles, scorecards, candidates, sources,
    interactions, sequences, and stage events with light consent/suppression
    checks. Intended for early prototyping; swap out with a fuller ORM later.
Dependencies:
    Standard library sqlite3/json/uuid plus local migration runner.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .migrations import apply_migrations, DEFAULT_MIGRATIONS_DIR


def _now() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()


def _dump_list(values: Optional[List[Any]]) -> str:
    return json.dumps(values or [])


def _dump_dict(values: Optional[Dict[str, Any]]) -> str:
    return json.dumps(values or {})


def _json_or_empty(raw: Any) -> Any:
    return json.loads(raw) if raw else []


class DataStore:
    def __init__(
        self,
        db_path: str = ":memory:",
        *,
        run_migrations: bool = True,
        migrations_dir=DEFAULT_MIGRATIONS_DIR,
    ) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        if run_migrations:
            apply_migrations(
                self.db_path, migrations_dir=migrations_dir, connection=self.conn
            )

    # --- candidate CRUD ---
    def create_candidate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = payload.get("id", str(uuid4()))
        now = _now()
        self.conn.execute(
            """
            INSERT INTO candidates (
                id, full_name, current_title, titles, years_experience, skills,
                domains, locations, timezone, remote_preference, stage_preferences,
                linkedin_url, email, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_id,
                payload["full_name"],
                payload.get("current_title"),
                _dump_list(payload.get("titles")),
                int(payload.get("years_experience", 0)),
                _dump_list(payload.get("skills")),
                _dump_list(payload.get("domains")),
                _dump_list(payload.get("locations")),
                payload.get("timezone"),
                int(payload["remote_preference"])
                if payload.get("remote_preference") is not None
                else None,
                _dump_list(payload.get("stage_preferences")),
                payload.get("linkedin_url"),
                payload.get("email"),
                now,
            ),
        )
        self.conn.commit()
        return self.get_candidate(candidate_id) or {}

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "full_name": row["full_name"],
            "current_title": row["current_title"],
            "titles": _json_or_empty(row["titles"]),
            "years_experience": row["years_experience"],
            "skills": _json_or_empty(row["skills"]),
            "domains": _json_or_empty(row["domains"]),
            "locations": _json_or_empty(row["locations"]),
            "timezone": row["timezone"],
            "remote_preference": (
                bool(row["remote_preference"])
                if row["remote_preference"] is not None
                else None
            ),
            "stage_preferences": _json_or_empty(row["stage_preferences"]),
            "linkedin_url": row["linkedin_url"],
            "email": row["email"],
            "created_at": row["created_at"],
        }

    def list_candidates(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM candidates").fetchall()
        return [self.get_candidate(row["id"]) or {} for row in rows]

    def update_candidate(
        self, candidate_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        fields = []
        values: List[Any] = []
        mapping = {
            "full_name": "full_name",
            "current_title": "current_title",
            "titles": ("titles", _dump_list),
            "years_experience": ("years_experience", int),
            "skills": ("skills", _dump_list),
            "domains": ("domains", _dump_list),
            "locations": ("locations", _dump_list),
            "timezone": "timezone",
            "remote_preference": (
                "remote_preference",
                lambda v: int(v) if v is not None else None,
            ),
            "stage_preferences": ("stage_preferences", _dump_list),
            "linkedin_url": "linkedin_url",
            "email": "email",
        }
        for key, db_field in mapping.items():
            if key not in updates:
                continue
            column, transform = (
                db_field if isinstance(db_field, tuple) else (db_field, lambda v: v)
            )
            fields.append(f"{column} = ?")
            values.append(transform(updates[key]))
        if not fields:
            return self.get_candidate(candidate_id)

        values.append(candidate_id)
        self.conn.execute(
            f"UPDATE candidates SET {', '.join(fields)} WHERE id = ?", values
        )
        self.conn.commit()
        return self.get_candidate(candidate_id)

    def delete_candidate(self, candidate_id: str) -> None:
        self.conn.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        self.conn.commit()

    # --- startup / role / scorecard ---
    def create_startup(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        startup_id = payload.get("id", str(uuid4()))
        now = _now()
        self.conn.execute(
            """
            INSERT INTO startups (
                id, name, stage, domains, location, description, website,
                mission, stack, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                startup_id,
                payload["name"],
                payload["stage"],
                _dump_list(payload.get("domains")),
                payload.get("location"),
                payload.get("description"),
                payload.get("website"),
                payload.get("mission"),
                _dump_list(payload.get("stack")),
                now,
            ),
        )
        self.conn.commit()
        return self.get_startup(startup_id) or {}

    def get_startup(self, startup_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM startups WHERE id = ?", (startup_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "name": row["name"],
            "stage": row["stage"],
            "domains": _json_or_empty(row["domains"]),
            "location": row["location"],
            "description": row["description"],
            "website": row["website"],
            "mission": row["mission"],
            "stack": _json_or_empty(row["stack"]),
            "created_at": row["created_at"],
        }

    def create_role(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        role_id = payload.get("id", str(uuid4()))
        now = _now()
        self.conn.execute(
            """
            INSERT INTO roles (
                id, startup_id, title, required_skills, nice_to_have_skills,
                min_years_experience, responsibilities, seniority,
                location_preference, remote_ok, compensation_range, recruiter_notes,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                role_id,
                payload["startup_id"],
                payload["title"],
                _dump_list(payload.get("required_skills")),
                _dump_list(payload.get("nice_to_have_skills")),
                int(payload.get("min_years_experience", 0)),
                _dump_list(payload.get("responsibilities")),
                payload.get("seniority", "vp"),
                payload.get("location_preference"),
                int(payload.get("remote_ok", True)),
                payload.get("compensation_range"),
                payload.get("recruiter_notes"),
                now,
            ),
        )
        self.conn.commit()
        return self.get_role(role_id) or {}

    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM roles WHERE id = ?", (role_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "startup_id": row["startup_id"],
            "title": row["title"],
            "required_skills": _json_or_empty(row["required_skills"]),
            "nice_to_have_skills": _json_or_empty(row["nice_to_have_skills"]),
            "min_years_experience": row["min_years_experience"],
            "responsibilities": _json_or_empty(row["responsibilities"]),
            "seniority": row["seniority"],
            "location_preference": row["location_preference"],
            "remote_ok": bool(row["remote_ok"]),
            "compensation_range": row["compensation_range"],
            "recruiter_notes": row["recruiter_notes"],
            "created_at": row["created_at"],
        }

    def list_roles(self, startup_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if startup_id:
            rows = self.conn.execute(
                "SELECT * FROM roles WHERE startup_id = ?", (startup_id,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM roles").fetchall()
        return [self.get_role(row["id"]) or {} for row in rows]

    def update_role(
        self, role_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        fields = []
        values: List[Any] = []
        mapping = {
            "title": "title",
            "required_skills": ("required_skills", _dump_list),
            "nice_to_have_skills": ("nice_to_have_skills", _dump_list),
            "min_years_experience": ("min_years_experience", int),
            "responsibilities": ("responsibilities", _dump_list),
            "seniority": "seniority",
            "location_preference": "location_preference",
            "remote_ok": ("remote_ok", lambda v: int(bool(v))),
            "compensation_range": "compensation_range",
            "recruiter_notes": "recruiter_notes",
        }
        for key, db_field in mapping.items():
            if key not in updates:
                continue
            column, transform = (
                db_field if isinstance(db_field, tuple) else (db_field, lambda v: v)
            )
            fields.append(f"{column} = ?")
            values.append(transform(updates[key]))
        if not fields:
            return self.get_role(role_id)
        values.append(role_id)
        self.conn.execute(f"UPDATE roles SET {', '.join(fields)} WHERE id = ?", values)
        self.conn.commit()
        return self.get_role(role_id)

    def delete_role(self, role_id: str) -> None:
        self.conn.execute("DELETE FROM roles WHERE id = ?", (role_id,))
        self.conn.commit()

    def create_scorecard(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        scorecard_id = payload.get("id", str(uuid4()))
        now = _now()
        self.conn.execute(
            """
            INSERT INTO scorecards (
                id, role_id, summary, must_haves, nice_to_haves, evaluation_points,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scorecard_id,
                payload["role_id"],
                payload.get("summary"),
                _dump_list(payload.get("must_haves")),
                _dump_list(payload.get("nice_to_haves")),
                _dump_list(payload.get("evaluation_points")),
                now,
            ),
        )
        self.conn.commit()
        return self.get_scorecard(scorecard_id) or {}

    def get_scorecard(self, scorecard_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM scorecards WHERE id = ?", (scorecard_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "role_id": row["role_id"],
            "summary": row["summary"],
            "must_haves": _json_or_empty(row["must_haves"]),
            "nice_to_haves": _json_or_empty(row["nice_to_haves"]),
            "evaluation_points": _json_or_empty(row["evaluation_points"]),
            "created_at": row["created_at"],
        }

    def list_scorecards(self, role_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if role_id:
            rows = self.conn.execute(
                "SELECT * FROM scorecards WHERE role_id = ?", (role_id,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM scorecards").fetchall()
        return [self.get_scorecard(row["id"]) or {} for row in rows]

    # --- sourcing and outreach primitives ---
    def add_profile_source(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source_id = payload.get("id", str(uuid4()))
        now = payload.get("imported_at") or _now()
        self.conn.execute(
            """
            INSERT INTO profile_sources (
                id, candidate_id, source, handle, url, notes, imported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                payload["candidate_id"],
                payload["source"],
                payload.get("handle"),
                payload.get("url"),
                payload.get("notes"),
                now,
            ),
        )
        self.conn.commit()
        return self.get_profile_source(source_id) or {}

    def get_profile_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM profile_sources WHERE id = ?", (source_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "candidate_id": row["candidate_id"],
            "source": row["source"],
            "handle": row["handle"],
            "url": row["url"],
            "notes": row["notes"],
            "imported_at": row["imported_at"],
        }

    def log_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = payload["candidate_id"]
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            raise ValueError("candidate not found")

        contact = (payload.get("metadata") or {}).get("contact") or candidate.get(
            "email"
        )
        if contact and self.is_suppressed(contact):
            self.record_audit_event(
                event_type="interaction_blocked",
                subject_id=candidate_id,
                detail={
                    "contact": contact,
                    "channel": payload.get("channel"),
                    "reason": "suppressed",
                },
            )
            raise PermissionError(f"contact {contact} is suppressed")

        interaction_id = payload.get("id", str(uuid4()))
        occurred_at = payload.get("occurred_at") or _now()
        self.conn.execute(
            """
            INSERT INTO interactions (
                id, candidate_id, channel, direction, subject, body, status,
                outcome, metadata, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                interaction_id,
                candidate_id,
                payload["channel"],
                payload["direction"],
                payload.get("subject"),
                payload.get("body"),
                payload.get("status"),
                payload.get("outcome"),
                _dump_dict(payload.get("metadata")),
                occurred_at,
            ),
        )
        self.conn.commit()
        return self.get_interaction(interaction_id) or {}

    def get_interaction(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM interactions WHERE id = ?", (interaction_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "candidate_id": row["candidate_id"],
            "channel": row["channel"],
            "direction": row["direction"],
            "subject": row["subject"],
            "body": row["body"],
            "status": row["status"],
            "outcome": row["outcome"],
            "metadata": json.loads(row["metadata"] or "{}"),
            "occurred_at": row["occurred_at"],
        }

    def list_interactions(
        self, candidate_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if candidate_id:
            rows = self.conn.execute(
                "SELECT * FROM interactions WHERE candidate_id = ? ORDER BY occurred_at",
                (candidate_id,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM interactions ORDER BY occurred_at"
            ).fetchall()
        return [self.get_interaction(row["id"]) or {} for row in rows]

    def create_sequence(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        sequence_id = payload.get("id", str(uuid4()))
        now = payload.get("created_at") or _now()
        self.conn.execute(
            """
            INSERT INTO sequences (id, role_id, name, steps, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                sequence_id,
                payload["role_id"],
                payload["name"],
                _dump_list(payload.get("steps")),
                int(payload.get("active", True)),
                now,
            ),
        )
        self.conn.commit()
        return self.get_sequence(sequence_id) or {}

    def get_sequence(self, sequence_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM sequences WHERE id = ?", (sequence_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "role_id": row["role_id"],
            "name": row["name"],
            "steps": _json_or_empty(row["steps"]),
            "active": bool(row["active"]),
            "created_at": row["created_at"],
        }

    def list_sequences(self, role_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if role_id:
            rows = self.conn.execute(
                "SELECT * FROM sequences WHERE role_id = ?", (role_id,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM sequences").fetchall()
        return [self.get_sequence(row["id"]) or {} for row in rows]

    def record_stage_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event_id = payload.get("id", str(uuid4()))
        occurred_at = payload.get("occurred_at") or _now()
        self.conn.execute(
            """
            INSERT INTO stage_events (
                id, candidate_id, role_id, stage, status, notes, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                payload["candidate_id"],
                payload["role_id"],
                payload["stage"],
                payload.get("status"),
                payload.get("notes"),
                occurred_at,
            ),
        )
        self.conn.commit()
        return self.get_stage_event(event_id) or {}

    def get_stage_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM stage_events WHERE id = ?", (event_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "candidate_id": row["candidate_id"],
            "role_id": row["role_id"],
            "stage": row["stage"],
            "status": row["status"],
            "notes": row["notes"],
            "occurred_at": row["occurred_at"],
        }

    def list_stage_events(self, candidate_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM stage_events WHERE candidate_id = ? ORDER BY occurred_at",
            (candidate_id,),
        ).fetchall()
        return [self.get_stage_event(row["id"]) or {} for row in rows]

    # --- suppression and consent scaffolding ---
    def suppress_contact(
        self, contact: str, reason: str | None = None, source: str | None = None
    ) -> None:
        now = _now()
        self.conn.execute(
            """
            INSERT OR REPLACE INTO suppression_list (contact, reason, source, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (contact.lower(), reason, source, now),
        )
        self.conn.commit()
        self.record_audit_event(
            event_type="suppression_added",
            subject_id=contact.lower(),
            detail={"reason": reason, "source": source},
        )

    def is_suppressed(self, contact: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM suppression_list WHERE contact = ?", (contact.lower(),)
        ).fetchone()
        return bool(row)

    def record_consent_event(
        self,
        *,
        contact: str,
        status: str,
        candidate_id: Optional[str] = None,
        source: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        event_id = str(uuid4())
        recorded_at = _now()
        self.conn.execute(
            """
            INSERT INTO consent_events (id, contact, candidate_id, status, source, notes, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                contact.lower(),
                candidate_id,
                status,
                source,
                notes,
                recorded_at,
            ),
        )
        self.conn.commit()
        return self.get_consent_event(event_id) or {}

    def get_consent_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM consent_events WHERE id = ?", (event_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "contact": row["contact"],
            "candidate_id": row["candidate_id"],
            "status": row["status"],
            "source": row["source"],
            "notes": row["notes"],
            "recorded_at": row["recorded_at"],
        }

    def record_audit_event(
        self,
        *,
        event_type: str,
        subject_id: Optional[str],
        detail: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        audit_id = str(uuid4())
        created_at = _now()
        self.conn.execute(
            """
            INSERT INTO audit_logs (id, event_type, subject_id, detail, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (audit_id, event_type, subject_id, _dump_dict(detail), created_at),
        )
        self.conn.commit()
        return self.get_audit_event(audit_id) or {}

    def get_audit_event(self, audit_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM audit_logs WHERE id = ?", (audit_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "event_type": row["event_type"],
            "subject_id": row["subject_id"],
            "detail": json.loads(row["detail"] or "{}"),
            "created_at": row["created_at"],
        }

    def list_audit_events(
        self, event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if event_type:
            rows = self.conn.execute(
                "SELECT * FROM audit_logs WHERE event_type = ? ORDER BY created_at DESC",
                (event_type,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM audit_logs ORDER BY created_at DESC"
            ).fetchall()
        return [self.get_audit_event(row["id"]) or {} for row in rows]

    def close(self) -> None:
        self.conn.close()
