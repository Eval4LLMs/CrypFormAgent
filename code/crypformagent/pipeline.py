"""Offline CrypFormAgent artifact pipeline.

This module wires the public interfaces into a deterministic harness.  It is
small by design: artifact readers can execute the full control flow without API
keys or verifier binaries, while replacing any component with the corresponding
research implementation keeps the same data contracts.
"""

import json
from pathlib import Path

from .ir import CrypIR
from .llm import OfflineReferenceProvider
from .lowering import ReferenceLowerer
from .ranking import Candidate, Ranker
from .repair import Repairer
from .verifier import OfflineVerifierAdapter


class PipelineResult(object):
    def __init__(self, cryp_ir, target, scaffold, candidates, selected, score):
        self.cryp_ir = cryp_ir
        self.target = target
        self.scaffold = scaffold
        self.candidates = list(candidates)
        self.selected = selected
        self.score = score

    def to_dict(self):
        return {
            "scheme": self.cryp_ir.name,
            "target": self.target,
            "cryp_ir": self.cryp_ir.to_dict(),
            "scaffold": {
                "language": self.scaffold.language,
                "text": self.scaffold.text,
                "notes": self.scaffold.notes,
                "metadata": self.scaffold.metadata,
            },
            "selected_score": self.score,
            "selected": self.selected.to_dict(score=self.score) if self.selected else None,
            "candidates": [
                candidate.to_dict(score=Ranker().score(candidate)) for candidate in self.candidates
            ],
        }


class ArtifactPipeline(object):
    def __init__(
        self,
        lowerer=None,
        provider=None,
        verifier=None,
        repairer=None,
        ranker=None,
        candidate_count=1,
    ):
        self.lowerer = lowerer or ReferenceLowerer()
        self.provider = provider or OfflineReferenceProvider()
        self.verifier = verifier or OfflineVerifierAdapter()
        self.repairer = repairer or Repairer()
        self.ranker = ranker or Ranker()
        self.candidate_count = max(1, int(candidate_count))

    def run(self, cryp_ir, target):
        scaffold = self.lowerer.lower(cryp_ir, target)
        prompt = build_prompt(cryp_ir, scaffold.language)
        candidates = []
        for index in range(self.candidate_count):
            generated = self.provider.generate(prompt, scaffold)
            verification = self.verifier.verify(generated.text, scaffold.language)
            repair = self.repairer.repair(generated.text, cryp_ir, verification)
            repaired_verification = self.verifier.verify(repair.artifact, scaffold.language)
            metadata = dict(generated.metadata)
            metadata["candidate_index"] = index
            candidates.append(
                Candidate(
                    artifact=repair.artifact,
                    verification=repaired_verification,
                    notes=scaffold.notes + repair.notes,
                    metadata=metadata,
                )
            )
        selected = self.ranker.rank(candidates)
        score = self.ranker.score(selected) if selected else 0.0
        return PipelineResult(cryp_ir, scaffold.language, scaffold, candidates, selected, score)


def build_prompt(cryp_ir, target):
    goals = ", ".join(goal.kind for goal in cryp_ir.goals) or "executable trace"
    return (
        "Generate a {target} formal artifact for {scheme}. "
        "Preserve roles, typed terms, message flow, adversary assumptions, "
        "and security goals: {goals}."
    ).format(target=target, scheme=cryp_ir.name, goals=goals)


def load_records(path, target=None, task=None, limit=None):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        records = data.get("records") or data.get("items") or data.get("data")
        if records is None:
            records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError("Unsupported JSON root in {}".format(path))

    selected = records[:limit] if limit else records
    return [CrypIR.from_dataset_record(record, target_language=target, task=task) for record in selected]


def write_json(path, data):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
