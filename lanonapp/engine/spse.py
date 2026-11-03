"""LaNonApp SPSE — SQLite event ledger and policy logic.

SPSE means Sistema Personal Situacional Escalable, NOT surveillance.
No sensor, contact sending, bank or clinical function exists in this module.

SPDX-License-Identifier: AGPL-3.0-or-later
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal, Mapping
import json
import sqlite3
import uuid

_MED_ACTIONS = {"refused", "deferred", "taken_self_reported", "unconfirmed"}
_RECEIPT_STEPS = ("local_intent_only", "queued", "provider_accepted", "delivered", "acknowledged", "resolved")
_REQUIRED_RECEIPTS = {"provider_accepted", "delivered", "acknowledged", "resolved"}

class PolicyError(ValueError):
    """A proposed transition or capability is not authorized or grounded."""

@dataclass(frozen=True)
class Incident:
    incident_id: str
    episode: str
    kind: str
    status: str
    recipient_id: str | None
    created_at: str
    receipt: str | None

@dataclass(frozen=True)
class Capability:
    name: str
    provider: str
    status: Literal['verified', 'experimental', 'conditional', 'not_supported', 'not_tested']
    required_scope: str
    geography: tuple[str, ...]
    verified_at: str | None
    limitations: tuple[str, ...]

class CapabilityRegistry:
    """Fail-closed platform contract; does not imply API connectivity."""
    def __init__(self) -> None:
        self._items: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        if not capability.name or not capability.provider:
            raise PolicyError('Una capacidad necesita proveedor y nombre')
        if capability.status == 'verified' and not capability.verified_at:
            raise PolicyError('La capacidad verificada requiere fecha y evidencia externa')
        self._items[capability.name] = capability

    def can_route(self, capability_name: str, region: str, valid_scopes: frozenset[str]) -> bool:
        c = self._items.get(capability_name)
        return bool(c and c.status == 'verified' and c.required_scope in valid_scopes and
                    (not c.geography or region in c.geography))

    def describe(self, name: str) -> Capability | None:
        return self._items.get(name)

class EventStore:
    """Transactional append-only event ledger with local incident intent.

    Storage is NOT encrypted. Do not put real medical/personal data here.
    Does not authenticate persons or verify legal authority: `verified` means an
    external process ASSERTED verification; no actual external verifier is wired.
    """

    def __init__(self, location: str | Path) -> None:
        self.path = str(location)
        if self.path != ':memory:':
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys=ON')
        if self.path != ':memory:':
            self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.executescript('''
          CREATE TABLE IF NOT EXISTS event (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            kind TEXT NOT NULL,
            source TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            received_at TEXT NOT NULL,
            payload TEXT NOT NULL,
            interaction_id TEXT NOT NULL,
            episode TEXT NOT NULL DEFAULT '',
            UNIQUE(subject, kind, episode, interaction_id)
          );
          CREATE INDEX IF NOT EXISTS idx_event_episode ON event(subject, episode, kind);
          CREATE TABLE IF NOT EXISTS grant_record (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            actor TEXT NOT NULL,
            scope TEXT NOT NULL,
            issuer_basis TEXT NOT NULL,
            verified INTEGER NOT NULL CHECK(verified IN (0,1)),
            valid_from TEXT NOT NULL,
            valid_to TEXT,
            revoked_at TEXT,
            UNIQUE(subject, actor, scope, valid_from)
          );
          CREATE TABLE IF NOT EXISTS incident (
            id TEXT PRIMARY KEY,
            episode TEXT NOT NULL,
            subject TEXT NOT NULL,
            kind TEXT NOT NULL,
            status TEXT NOT NULL,
            recipient TEXT,
            created_at TEXT NOT NULL,
            receipt TEXT,
            UNIQUE(subject, episode, kind)
          );
          CREATE TABLE IF NOT EXISTS receipt_history (
            id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL REFERENCES incident(id),
            old_status TEXT NOT NULL,
            new_status TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            evidence TEXT NOT NULL
          );
        ''')

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _ensure_iso(value: str) -> str:
        try:
            date = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError) as ex:
            raise PolicyError('Tiempo inválido') from ex
        if date.tzinfo is None or date.utcoffset() is None:
            raise PolicyError('Tiempo sin zona horaria')
        return date.astimezone(timezone.utc).isoformat()

    def close(self) -> None:
        self.conn.close()

    def add_grant(self, *, subject: str, actor: str, scope: str, issuer_basis: str,
                  verified: bool, valid_from: str, valid_to: str | None = None) -> str:
        valid_from = self._ensure_iso(valid_from)
        if valid_to: valid_to = self._ensure_iso(valid_to)
        if not subject or not actor or not scope or not issuer_basis:
            raise PolicyError('Concedente, sujeto, actor, competencia y fundamento deben documentarse')
        if valid_to and valid_to <= valid_from:
            raise PolicyError('Delegación temporal inválida')
        id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute('INSERT INTO grant_record VALUES (?,?,?,?,?,?,?,?,?)',
                              (id, subject, actor, scope, issuer_basis, int(verified), valid_from, valid_to, None))
        return id

    def revoke_grant(self, grant_id: str, observed_at: str | None = None) -> bool:
        ts = observed_at or self._now()
        ts = self._ensure_iso(ts)
        with self.conn:
            cur = self.conn.execute('UPDATE grant_record SET revoked_at=? WHERE id=? AND revoked_at IS NULL',
                                    (ts, grant_id))
        return bool(cur.rowcount)

    def authorized(self, subject: str, actor: str, scope: str, at: str | None = None) -> bool:
        at = at or self._now()
        at = self._ensure_iso(at)
        q = self.conn.execute('''SELECT count(*) n FROM grant_record
          WHERE subject=? AND actor=? AND scope=? AND verified=1
            AND valid_from<=? AND (valid_to IS NULL OR valid_to>=?)
            AND (revoked_at IS NULL OR revoked_at>?)''', (subject, actor, scope, at, at, at)).fetchone()
        return bool(q['n'])

    def append_event(self, *, subject: str, kind: str, source: str,
                     observed_at: str, interaction_id: str, payload: Mapping,
                     episode: str | None = None) -> tuple[str, bool]:
        observed_at = self._ensure_iso(observed_at)
        episode = episode or ''
        if not all([subject, kind, source, interaction_id]) or not isinstance(payload, Mapping):
            raise PolicyError('Evento sin identidad, fuente, interacción o payload')
        if len(json.dumps(payload, ensure_ascii=False)) > 30000:
            raise PolicyError('Evento excesivo')
        id = str(uuid.uuid4())
        with self.conn:
            cur = self.conn.execute('''INSERT OR IGNORE INTO event VALUES (?,?,?,?,?,?,?,?,?)''',
                                    (id, subject, kind, source, observed_at, self._now(),
                                     json.dumps(dict(payload), ensure_ascii=False), interaction_id, episode))
            if not cur.rowcount:
                old = self.conn.execute('''SELECT id, payload, source FROM event WHERE subject=? AND kind=?
                    AND episode=? AND interaction_id=?''', (subject, kind, episode, interaction_id)).fetchone()
                if not old:
                    raise PolicyError('Conflicto de idempotencia')
                if json.loads(old['payload']) != dict(payload) or old['source'] != source:
                    raise PolicyError('Reutilización conflictiva de identificador de interacción')
                return old['id'], False
        return id, True

    def record_medication_response(self, *, subject: str, episode: str,
                                   action: str, interaction_id: str,
                                   observed_at: str, recipient_id: str | None,
                                   plan_version: str) -> Incident | None:
        """Two distinct explicit refusals/deferments => local intent, not transmitted.

        Condition is an illustrative configurable policy for a verified plan;
        this function is NOT clinical guidance or a dose decision.
        """
        if action not in _MED_ACTIONS or not episode or not plan_version:
            raise PolicyError('Acción, episodio o plan inválido')
        with self.conn:
            # Ignore repeated utterance or retry across action types.
            previous = self.conn.execute('''SELECT id FROM event WHERE subject=? AND episode=?
                AND interaction_id=? AND kind LIKE 'med.%' LIMIT 1''',
                (subject, episode, interaction_id)).fetchone()
            if previous:
                return self._incident_for_episode(subject, episode)
            if self.conn.execute('''SELECT 1 FROM event WHERE subject=? AND episode=?
                AND kind='med.taken_self_reported' LIMIT 1''', (subject, episode)).fetchone():
                raise PolicyError('Episodio ya marcado tomado: requiere revisión explícita')
            self.append_event(subject=subject, kind='med.'+action, source='user_reported',
                              observed_at=observed_at, interaction_id=interaction_id,
                              payload={'plan_version': plan_version}, episode=episode)
            if action not in {'refused', 'deferred'}:
                return None
            n = self.conn.execute('''SELECT COUNT(DISTINCT interaction_id) n FROM event
                  WHERE subject=? AND episode=? AND kind IN ('med.refused','med.deferred')''',
                  (subject, episode)).fetchone()['n']
            if n < 2:
                return None
            existing = self._incident_for_episode(subject, episode)
            if existing:
                return existing
            id = 'spse:' + str(uuid.uuid4())
            self.conn.execute('''INSERT INTO incident VALUES (?,?,?,?,?,?,?,?)''',
                              (id, episode, subject, 'medication_followup',
                               'local_intent_only', recipient_id, self._now(), None))
            return self._incident_for_episode(subject, episode)

    def _incident_for_episode(self, subject: str, episode: str) -> Incident | None:
        row = self.conn.execute('''SELECT * FROM incident WHERE subject=? AND episode=?
          AND kind='medication_followup' ''', (subject, episode)).fetchone()
        return Incident(row['id'],row['episode'],row['kind'],row['status'],row['recipient'],row['created_at'],row['receipt']) if row else None

    def transition_incident(self, incident_id: str, new_state: str, *,
                            actor: str, subject: str, evidence: str | None = None) -> Incident:
        if new_state not in _RECEIPT_STEPS:
            raise PolicyError('Estado no contemplado')
        if not self.authorized(subject, actor, 'spse.dispatch'):
            raise PolicyError('Actor sin competencia verificada spse.dispatch')
        with self.conn:
            row = self.conn.execute('SELECT * FROM incident WHERE id=? AND subject=?',
                                    (incident_id, subject)).fetchone()
            if not row:
                raise PolicyError('Incidente desconocido')
            old = row['status']
            if old == new_state:
                return Incident(row['id'],row['episode'],row['kind'],old,row['recipient'],row['created_at'],row['receipt'])
            if new_state not in _RECEIPT_STEPS or _RECEIPT_STEPS.index(new_state) != _RECEIPT_STEPS.index(old)+1:
                raise PolicyError('Transición de estado no autorizada')
            if new_state in _REQUIRED_RECEIPTS and not evidence:
                raise PolicyError('No se puede afirmar un recibo sin evidencia')
            self.conn.execute('UPDATE incident SET status=?, receipt=? WHERE id=?',
                              (new_state, evidence or row['receipt'], incident_id))
            self.conn.execute('INSERT INTO receipt_history VALUES (?,?,?,?,?,?)',
                              (str(uuid.uuid4()), incident_id, old, new_state,self._now(),evidence or 'local_transition'))
            row = self.conn.execute('SELECT * FROM incident WHERE id=?',(incident_id,)).fetchone()
            return Incident(row['id'],row['episode'],row['kind'],row['status'],row['recipient'],row['created_at'],row['receipt'])

    def list_events(self, subject: str, *, limit: int = 100) -> list[dict]:
        if limit <= 0 or limit > 1000:
            raise PolicyError('Límite fuera de rango')
        rows=self.conn.execute('''SELECT * FROM event WHERE subject=? ORDER BY received_at DESC LIMIT ?''',(subject,limit)).fetchall()
        return [dict(r) | {'payload': json.loads(r['payload'])} for r in rows]


def conditional_cashflow(*, currency: str, cash: Decimal | str,
                         monthly_income: Decimal | str, monthly_outflows: Decimal | str,
                         months: int, exceptional: Decimal | str, reserve: Decimal | str) -> dict:
    """Exact conditional arithmetic for one currency, not probabilistic forecasting."""
    if not currency or not currency.isalpha() or len(currency) != 3:
        raise PolicyError('Se requiere una moneda ISO-4217 única')
    if not isinstance(months, int) or isinstance(months,bool) or not 0 <= months <= 1200:
        raise PolicyError('Horizonte temporal inválido')
    try:
        cs = [Decimal(v) for v in (cash, monthly_income, monthly_outflows, exceptional, reserve)]
    except (InvalidOperation, ValueError, TypeError) as e:
        raise PolicyError('Falta un importe real y numérico') from e
    if not all(x.is_finite() for x in cs) or any(cs[i] < 0 for i in (2,3,4)):
        raise PolicyError('Parámetros inválidos')
    c,inc,out,xtra,minimum=cs
    bal=c + months*(inc-out) - xtra
    return {'currency': currency.upper(), 'balance':str(bal),
            'available_above_reserve':str(bal-minimum), 'monthly_net_flow':str(inc-out),
            'kind':'conditional_deterministic_not_a_forecast',
            'inputs':dict(zip(('cash','monthly_income','monthly_outflows','exceptional','reserve'),map(str,cs))),
            'months':months, 'data_provenance':'caller_supplied_unverified'}