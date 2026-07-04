"""Target-language lowering interfaces for the public artifact."""


class ArtifactScaffold(object):
    def __init__(self, language, text, notes=None, metadata=None):
        self.language = language
        self.text = text
        self.notes = list(notes or [])
        self.metadata = metadata or {}


class Lowerer(object):
    """Map a CrypIR object into a target-language scaffold."""

    def lower(self, cryp_ir, target_language):
        """Return a target-language scaffold."""
        raise NotImplementedError


class ReferenceLowerer(Lowerer):
    """Deterministic offline lowerer used by the artifact harness.

    The full CrypFormAgent system uses verifier-specific lowerers.  This
    reference lowerer preserves the same orchestration boundary and renders
    auditable target-language skeletons from CrypIR so that artifact readers can
    inspect inputs, control flow, verifier normalization, repair, and ranking
    without external theorem-prover installations.
    """

    SUPPORTED = set(["spdl", "spthy", "pv", "hlpsl", "maude", "ec", "cv"])

    def lower(self, cryp_ir, target_language):
        language = target_language.lower()
        if language not in self.SUPPORTED:
            raise ValueError("Unsupported artifact target: {}".format(target_language))

        lines = self._render(language, cryp_ir)
        return ArtifactScaffold(
            language=language,
            text="\n".join(lines),
            notes=["reference lowering completed"],
            metadata={"scheme": cryp_ir.name, "target": language},
        )

    def _render(self, language, cryp_ir):
        if language == "spdl":
            return self._spdl(cryp_ir)
        if language == "spthy":
            return self._spthy(cryp_ir)
        if language == "pv":
            return self._pv(cryp_ir)
        if language == "hlpsl":
            return self._hlpsl(cryp_ir)
        if language == "maude":
            return self._maude(cryp_ir)
        if language == "ec":
            return self._ec(cryp_ir)
        return self._cv(cryp_ir)

    def _common_summary(self, cryp_ir, comment):
        lines = [
            "{} CrypFormAgent artifact lowering".format(comment),
            "{} Scheme: {}".format(comment, cryp_ir.name),
            "{} Source: {}".format(comment, cryp_ir.source_language or "logic"),
            "{} Summary: {}".format(comment, cryp_ir.summary()),
        ]
        if cryp_ir.metadata.get("source_file"):
            lines.append("{} Source file: {}".format(comment, cryp_ir.metadata["source_file"]))
        return lines

    def _spdl(self, cryp_ir):
        roles = ", ".join(cryp_ir.roles) or "Actor"
        lines = self._common_summary(cryp_ir, "//")
        lines.extend(["", "protocol {}({}) {{".format(cryp_ir.name, roles)])
        for role in cryp_ir.roles or ["Actor"]:
            lines.extend(["  role {} {{".format(role), "    fresh localNonce: Nonce;"])
            for idx, message in enumerate(_messages_for_role(cryp_ir, role), start=1):
                payload = ", ".join(message.payload) or "payload"
                direction = "send" if message.sender == role else "recv"
                peer = message.receiver if message.sender == role else message.sender
                lines.append("    {}_{}({}, {});".format(direction, idx, peer, payload))
            for idx, goal in enumerate(cryp_ir.goals, start=1):
                target = ", {}".format(goal.target) if goal.target else ""
                lines.append("    claim_{}({}, {}{});".format(idx, role, _spdl_claim(goal.kind), target))
            lines.append("  }")
        lines.append("}")
        return lines

    def _spthy(self, cryp_ir):
        lines = self._common_summary(cryp_ir, "//")
        lines.extend(["", "theory {}".format(cryp_ir.name), "begin", ""])
        for message in cryp_ir.messages:
            payload = "_".join(message.payload) or "Payload"
            lines.append("rule {}_{}_{}:".format(message.label or "Msg", message.sender, message.receiver))
            lines.append("  [ Fr(~n) ]")
            lines.append("  --[ Send('{}','{}','{}') ]->".format(message.sender, message.receiver, payload))
            lines.append("  [ Out(< '{}', '{}' >) ]".format(message.sender, payload))
            lines.append("")
        for goal in cryp_ir.goals or [None]:
            lines.append(_spthy_lemma(goal))
            lines.append("")
        lines.append("end")
        return lines

    def _pv(self, cryp_ir):
        lines = self._common_summary(cryp_ir, "(*")
        lines = [line + (" *)" if line.startswith("(*") else "") for line in lines]
        lines.extend(["", "free c: channel.", "type principal.", "type nonce.", ""])
        for term in cryp_ir.terms:
            lines.append("free {}: {} [private].".format(term.name, _pv_type(term.kind)))
        lines.append("")
        for goal in cryp_ir.goals:
            lines.append(_pv_query(goal))
        lines.extend(["", "process"])
        if cryp_ir.messages:
            rendered = []
            for message in cryp_ir.messages:
                payload = ", ".join(message.payload) or "payload"
                rendered.append("  out(c, ({}, {}, {}))".format(message.sender, message.receiver, payload))
            lines.append(" ;\n".join(rendered))
        else:
            lines.append("  0")
        return lines

    def _hlpsl(self, cryp_ir):
        lines = self._common_summary(cryp_ir, "%")
        lines.extend(["", "role session({}: agent, SND, RCV: channel(dy))".format(", ".join(cryp_ir.roles) or "A,B")])
        lines.extend(["played_by {}".format((cryp_ir.roles or ["A"])[0]), "def=", "  local State: nat", "  init State := 0", "  transition"])
        if cryp_ir.messages:
            for idx, message in enumerate(cryp_ir.messages, start=1):
                payload = ".".join(message.payload) or "Payload"
                lines.append("    {}. State = {} /\\ RCV({}) =|> State' := {} /\\ SND({})".format(idx, idx - 1, payload, idx, payload))
        else:
            lines.append("    1. State = 0 =|> State' := 1")
        lines.extend(["end role", "", "role environment()", "def=", "  composition", "    session()", "end role"])
        return lines

    def _maude(self, cryp_ir):
        module_name = "{}-ARTIFACT".format(cryp_ir.name.upper())
        lines = self._common_summary(cryp_ir, "---")
        lines.extend(["", "fmod {} is".format(module_name), "  sort Principal Nonce Msg ."])
        for role in cryp_ir.roles:
            lines.append("  op {} : -> Principal .".format(role))
        for message in cryp_ir.messages:
            payload = "_".join(message.payload) or "payload"
            lines.append("  op {}-{}-{} : -> Msg .".format(message.sender, message.receiver, payload))
        for goal in cryp_ir.goals:
            lines.append("  --- goal {} {}".format(goal.kind, goal.target or ""))
        lines.append("endfm")
        return lines

    def _ec(self, cryp_ir):
        lines = self._common_summary(cryp_ir, "(*")
        lines = [line + (" *)" if line.startswith("(*") else "") for line in lines]
        lines.extend(["", "theory {}.".format(cryp_ir.name), "type principal.", "type message.", ""])
        for goal in cryp_ir.goals:
            theorem = "{}_{}".format(goal.kind, goal.target or "goal").replace("-", "_")
            lines.append("axiom {} : true.".format(theorem))
        if not cryp_ir.goals:
            lines.append("axiom executable_trace : true.")
        lines.append("end.")
        return lines

    def _cv(self, cryp_ir):
        lines = self._common_summary(cryp_ir, "(*")
        lines = [line + (" *)" if line.startswith("(*") else "") for line in lines]
        lines.extend(["", "channel c.", "type principal.", "type bitstring.", ""])
        for goal in cryp_ir.goals:
            lines.append(_cv_query(goal))
        lines.extend(["", "process 0"])
        return lines


ToyLowerer = ReferenceLowerer


def _messages_for_role(cryp_ir, role):
    return [message for message in cryp_ir.messages if message.sender == role or message.receiver == role]


def _spdl_claim(kind):
    mapping = {
        "authentication": "Niagree",
        "agreement": "Niagree",
        "secrecy": "Secret",
        "secret": "Secret",
        "nisynch": "Nisynch",
        "niagree": "Niagree",
        "alive": "Alive",
        "weakagree": "Weakagree",
    }
    return mapping.get(str(kind).lower(), str(kind))


def _spthy_lemma(goal):
    if goal is None:
        return "lemma executable_trace: exists-trace \"Ex #i. True\""
    name = "{}_{}".format(goal.kind, goal.target or "goal").replace("-", "_")
    return "lemma {}: \"All x #i. {}(x) @ #i ==> not (Ex #j. K(x) @ #j)\"".format(name, goal.kind.capitalize())


def _pv_type(kind):
    if "nonce" in str(kind).lower():
        return "nonce"
    return "bitstring"


def _pv_query(goal):
    if str(goal.kind).lower() in set(["secrecy", "secret"]):
        return "query attacker({}).".format(goal.target or "secret_value")
    return "event {}_event(bitstring).".format(str(goal.kind).replace("-", "_"))


def _cv_query(goal):
    if str(goal.kind).lower() in set(["secrecy", "secret"]):
        return "query secret {}.".format(goal.target or "secret_value")
    return "event {}_event.".format(str(goal.kind).replace("-", "_"))
