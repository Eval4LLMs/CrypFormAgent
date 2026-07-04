"""Typed repair interface for the public artifact."""


class RepairResult(object):
    def __init__(self, artifact, notes=None):
        self.artifact = artifact
        self.notes = list(notes or [])


class Repairer(object):
    """Apply small deterministic repairs from normalized verifier feedback."""

    def repair(self, artifact, cryp_ir, result):
        if result.analyzable:
            return RepairResult(artifact=artifact, notes=["no repair requested"])
        repaired = artifact.rstrip() + "\n\n{}".format(_repair_note(cryp_ir, result))
        return RepairResult(artifact=repaired, notes=["offline repair note appended"])


def _repair_note(cryp_ir, result):
    detail = "; ".join(result.diagnostics) or "verifier reported a structural issue"
    return "// Repair evidence for {}: {}".format(cryp_ir.name, detail)
