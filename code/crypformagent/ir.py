"""Tool-neutral semantic objects used by the CrypFormAgent artifact.

The paper-level prototype builds richer CrypIR objects from natural-language
scheme descriptions and existing verifier code.  The public artifact keeps the
same boundary explicit: records are normalized into roles, typed terms, message
flows, adversary assumptions, and goals before any target-language rendering is
attempted.
"""


class Term(object):
    """A typed symbolic term used by a cryptographic scheme."""

    def __init__(self, name, kind, owner=None, metadata=None):
        self.name = name
        self.kind = kind
        self.owner = owner
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "name": self.name,
            "kind": self.kind,
            "owner": self.owner,
            "metadata": self.metadata,
        }


class Message(object):
    """A message-flow edge between two roles."""

    def __init__(self, sender, receiver, payload, label=None):
        self.sender = sender
        self.receiver = receiver
        self.payload = list(payload or [])
        self.label = label

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "payload": self.payload,
            "label": self.label,
        }


class Goal(object):
    """A security goal represented at the scheme level."""

    def __init__(self, kind, target=None, parties=None, expected_verdict=None):
        self.kind = kind
        self.target = target
        self.parties = list(parties or [])
        self.expected_verdict = expected_verdict

    def to_dict(self):
        return {
            "kind": self.kind,
            "target": self.target,
            "parties": self.parties,
            "expected_verdict": self.expected_verdict,
        }


class CrypIR(object):
    """A compact, tool-neutral representation of a formalization task."""

    def __init__(
        self,
        name,
        roles,
        terms,
        messages,
        adversary_assumptions,
        goals,
        source_language=None,
        target_language=None,
        metadata=None,
    ):
        self.name = name
        self.roles = list(roles or [])
        self.terms = list(terms or [])
        self.messages = list(messages or [])
        self.adversary_assumptions = list(adversary_assumptions or [])
        self.goals = list(goals or [])
        self.source_language = source_language
        self.target_language = target_language
        self.metadata = metadata or {}

    @classmethod
    def from_dict(cls, data, target_language=None):
        terms = [Term(**item) for item in data.get("terms", [])]
        messages = [Message(**item) for item in data.get("messages", [])]
        goals = [Goal(**item) for item in data.get("goals", [])]
        return cls(
            name=data.get("name", "unnamed-scheme"),
            roles=data.get("roles", []),
            terms=terms,
            messages=messages,
            adversary_assumptions=data.get("adversary_assumptions", []),
            goals=goals,
            source_language=data.get("source_language"),
            target_language=target_language or data.get("target_language"),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def from_dataset_record(cls, data, target_language=None, task=None):
        """Create a compact CrypIR object from a released dataset record.

        Dataset records in this repository intentionally preserve their
        task-facing shape.  They are not always fully structured CrypIR JSON.
        This adapter extracts the stable metadata available across task files
        and keeps the original text as provenance for offline artifact runs.
        """
        if "roles" in data or "terms" in data or "messages" in data:
            return cls.from_dict(data, target_language=target_language)

        source_file = data.get("file") or data.get("name") or "dataset-record"
        name = _normalize_name(source_file)
        roles, goals = _extract_result_goals(data.get("results"))
        source_language = _language_from_filename(source_file)
        metadata = {
            "task": task or data.get("task") or "dataset",
            "source_file": source_file,
            "logic_excerpt": _compact_text(data.get("logic") or data.get("description") or ""),
        }
        return cls(
            name=name,
            roles=roles,
            terms=[],
            messages=[],
            adversary_assumptions=[],
            goals=goals,
            source_language=source_language,
            target_language=target_language,
            metadata=metadata,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "roles": self.roles,
            "terms": [term.to_dict() for term in self.terms],
            "messages": [message.to_dict() for message in self.messages],
            "adversary_assumptions": self.adversary_assumptions,
            "goals": [goal.to_dict() for goal in self.goals],
            "source_language": self.source_language,
            "target_language": self.target_language,
            "metadata": self.metadata,
        }

    def summary(self):
        return "{}: {} roles, {} terms, {} messages, {} goals".format(
            self.name,
            len(self.roles),
            len(self.terms),
            len(self.messages),
            len(self.goals),
        )


def _extract_result_goals(results):
    roles = []
    goals = []
    for row in _walk_rows(results):
        if len(row) < 5:
            continue
        role = row[1]
        claim = row[3]
        status = row[4]
        if role and role not in roles:
            roles.append(role)
        if not claim:
            continue
        parts = str(claim).split(None, 1)
        kind = parts[0].lower()
        target = parts[1] if len(parts) > 1 else None
        verdict = "safe" if str(status).upper() == "OK" else "unsafe"
        goals.append(Goal(kind=kind, target=target, parties=list(roles), expected_verdict=verdict))
    return roles, goals


def _walk_rows(value):
    if isinstance(value, list):
        if value and all(not isinstance(item, (list, dict)) for item in value):
            yield value
        else:
            for item in value:
                for row in _walk_rows(item):
                    yield row


def _language_from_filename(filename):
    ext = str(filename).rsplit(".", 1)
    return ext[1].lower() if len(ext) == 2 else None


def _normalize_name(filename):
    stem = str(filename).rsplit("/", 1)[-1].rsplit(".", 1)[0]
    normalized = []
    for char in stem:
        normalized.append(char if char.isalnum() else "_")
    return "".join(normalized).strip("_") or "dataset_record"


def _compact_text(text, limit=1200):
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."
