"""Replaceable generation-provider interface for the artifact harness."""


class GenerationResult(object):
    def __init__(self, text, metadata=None):
        self.text = text
        self.metadata = metadata or {}


class LLMProvider(object):
    """Minimal provider contract used by CrypFormAgent orchestration."""

    def generate(self, prompt, scaffold):
        """Return one candidate artifact for the supplied prompt and scaffold."""
        raise NotImplementedError


class OfflineReferenceProvider(LLMProvider):
    """Deterministic offline provider for smoke tests and artifact review."""

    def generate(self, prompt, scaffold):
        body = scaffold.text.rstrip()
        text = body + "\n\n{}".format(_completion_note(scaffold.language))
        return GenerationResult(
            text=text,
            metadata={"provider": "offline-reference", "prompt_chars": len(prompt)},
        )


def _completion_note(language):
    if language in set(["pv", "ec", "cv"]):
        return "(* Offline reference candidate generated from CrypIR. *)"
    if language == "hlpsl":
        return "% Offline reference candidate generated from CrypIR."
    if language == "maude":
        return "--- Offline reference candidate generated from CrypIR."
    return "// Offline reference candidate generated from CrypIR."


MockLLMProvider = OfflineReferenceProvider
