"""Candidate ranking contract for the public artifact."""


class Candidate(object):
    def __init__(self, artifact, verification, notes=None, metadata=None):
        self.artifact = artifact
        self.verification = verification
        self.notes = list(notes or [])
        self.metadata = metadata or {}

    def to_dict(self, score=None):
        data = {
            "artifact": self.artifact,
            "verification": self.verification.to_dict(),
            "notes": self.notes,
            "metadata": self.metadata,
        }
        if score is not None:
            data["score"] = score
        return data


class Ranker(object):
    """Deterministic ranker over normalized verification signals."""

    def score(self, candidate):
        score = 0.0
        if candidate.verification.analyzable:
            score += 1.0
        if candidate.verification.status in set(["safe", "unsafe"]):
            score += 1.0
        if "compile_error" not in candidate.verification.status:
            score += 0.25
        return score

    def rank(self, candidates):
        items = list(candidates)
        if not items:
            return None
        return max(items, key=self.score)
