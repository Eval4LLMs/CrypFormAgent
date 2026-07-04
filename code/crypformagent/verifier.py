"""Verifier adapter contracts for the public artifact."""


class VerificationResult(object):
    def __init__(self, status, analyzable, diagnostics=None, runtime_seconds=0.0, metadata=None):
        self.status = status
        self.analyzable = analyzable
        self.diagnostics = list(diagnostics or [])
        self.runtime_seconds = runtime_seconds
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "status": self.status,
            "analyzable": self.analyzable,
            "diagnostics": self.diagnostics,
            "runtime_seconds": self.runtime_seconds,
            "metadata": self.metadata,
        }


class VerifierAdapter(object):
    """Normalize a target verifier result into a shared contract."""

    def verify(self, artifact, language):
        """Verify or analyze an artifact."""
        raise NotImplementedError


class OfflineVerifierAdapter(VerifierAdapter):
    """Offline verifier shim used when external tools are unavailable."""

    REQUIRED_MARKERS = {
        "spdl": ["protocol"],
        "spthy": ["theory", "begin", "end"],
        "pv": ["process"],
        "hlpsl": ["role", "transition"],
        "maude": ["fmod", "endfm"],
        "ec": ["theory", "end."],
        "cv": ["process"],
    }

    def verify(self, artifact, language):
        if not artifact.strip():
            return VerificationResult(
                status="compile_error",
                analyzable=False,
                diagnostics=["empty artifact"],
                metadata={"language": language},
            )
        markers = self.REQUIRED_MARKERS.get(str(language).lower(), [])
        missing = [marker for marker in markers if marker.lower() not in artifact.lower()]
        if missing:
            return VerificationResult(
                status="compile_error",
                analyzable=False,
                diagnostics=["missing language markers: {}".format(", ".join(missing))],
                metadata={"language": language, "adapter": "offline-reference"},
            )
        return VerificationResult(
            status="safe",
            analyzable=True,
            diagnostics=["offline verifier accepted structural markers"],
            metadata={"language": language, "adapter": "offline-reference"},
        )


MockVerifierAdapter = OfflineVerifierAdapter
