<h1 align="center">🧪 CrypFormAgent Code</h1>

<p align="center">
  <b>Executable Reference Implementation for the Public Artifact</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue">
  <img src="https://img.shields.io/badge/Dependencies-None-success">
  <img src="https://img.shields.io/badge/Mode-Offline%20Reference-orange">
  <img src="https://img.shields.io/badge/Targets-7%20Languages-purple">
</p>

> This directory makes the CrypFormAgent interfaces runnable without model API keys, verifier binaries, or third-party Python packages. It is a deterministic harness for inspecting the framework boundary used in the paper.

---

## 🔁 Pipeline

```text
task record
   |
   v
CrypIR
   |
   v
target-language scaffold
   |
   v
candidate artifact -> verifier signal -> typed repair -> ranking
   |
   v
JSON report
```

The quantitative results reported in the paper are backed by released traces and aggregate files under [`../html/`](../html/) and [`../results/`](../results/). This code focuses on reproducible interface execution and smoke testing.

---

## 🛠️ Environment & Deployment

The reference implementation is intentionally lightweight. It runs as a local Python module and does not install services, start a server, or require external verifier binaries.

| Item | Requirement |
| --- | --- |
| Python | 3.8 or newer |
| Python packages | Standard library only |
| Network access | Not required |
| Model credentials | Not required |
| Verifier binaries | Not required for the offline reference mode |
| Expected working directory | `CrypFormAgent/code` |
| Generated outputs | `artifacts/`, ignored by `.gitignore` |

Optional isolated environment:

```bash
cd CrypFormAgent/code
python3 -m venv .venv
source .venv/bin/activate
python3 -m unittest discover -s tests
```

No `pip install` step is needed for the released reference harness. To deploy a tool-backed variant, replace `OfflineReferenceProvider` or `OfflineVerifierAdapter` with project-specific adapters and keep generated logs, verifier scratch files, and model outputs outside the tracked source tree.

---

## 🚀 Quick Start

Run all commands from this directory:

```bash
cd CrypFormAgent/code
```

Run one structured CrypIR instance:

```bash
python3 -m crypformagent run \
  --input examples/minimal_generation.json \
  --target spdl \
  --output artifacts/smoke_spdl.json
```

Expected summary:

```text
CrypFormAgent reference run
Input: nonce_key_exchange: 2 roles, 4 terms, 3 messages, 2 goals
Target: spdl
Verifier: safe
Score: 2.25
```

Run a bounded batch over released dataset records:

```bash
python3 -m crypformagent batch \
  --input ../datasets/generation/spdl_datasets_data_eng_100.json \
  --target spdl \
  --limit 5 \
  --output artifacts/spdl_generation_batch.json
```

Run the tests:

```bash
python3 -m unittest discover -s tests
```

Generated reports are local artifacts and are ignored by `.gitignore`.

---

## 🗂️ Package Map

| Path | Purpose |
| --- | --- |
| `crypformagent/__main__.py` | Module entry point for `python3 -m crypformagent`. |
| `crypformagent/cli.py` | CLI for single-instance and batch runs. |
| `crypformagent/pipeline.py` | End-to-end pipeline and report serialization. |
| `crypformagent/ir.py` | CrypIR data model and adapter for released dataset records. |
| `crypformagent/lowering.py` | Deterministic reference lowerer for seven target languages. |
| `crypformagent/llm.py` | Replaceable generation-provider contract and offline provider. |
| `crypformagent/verifier.py` | Verifier-adapter contract and offline structural checker. |
| `crypformagent/repair.py` | Typed repair hook over normalized verifier diagnostics. |
| `crypformagent/ranking.py` | Candidate representation and deterministic ranker. |
| `examples/` | Minimal structured CrypIR input for smoke testing. |
| `configs/` | Offline artifact configuration template. |
| `tests/` | Standard-library unit tests. |

---

## 🧭 Command Reference

```bash
python3 -m crypformagent [run|batch] --input PATH [options]
```

| Option | Meaning |
| --- | --- |
| `run` | Execute one record. This is the default command. |
| `batch` | Execute a bounded prefix of records from a JSON list. |
| `--input PATH` | Structured CrypIR JSON or released dataset JSON. |
| `--target LANG` | Target language: `spdl`, `spthy`, `pv`, `hlpsl`, `maude`, `ec`, or `cv`. |
| `--task NAME` | Task label stored in the output report. Default: `generation`. |
| `--index N` | Record index for `run` when the input is a JSON list. |
| `--limit N` | Maximum number of records for `batch`. Default: `5`. |
| `--candidates N` | Number of deterministic offline candidates. Default: `1`. |
| `--output PATH` | Optional JSON report path. |

---

## 📥 Input Formats

### Structured CrypIR JSON

`examples/minimal_generation.json` shows the explicit schema expected by the pipeline:

```json
{
  "name": "nonce_key_exchange",
  "roles": ["A", "B"],
  "terms": [
    {"name": "na", "kind": "nonce", "owner": "A"}
  ],
  "messages": [
    {"label": "m1", "sender": "A", "receiver": "B", "payload": ["A", "na"]}
  ],
  "adversary_assumptions": ["active Dolev-Yao network adversary"],
  "goals": [
    {"kind": "secrecy", "target": "kab", "parties": ["A", "B"], "expected_verdict": "safe"}
  ],
  "source_language": "logic"
}
```

### Released Dataset Records

Dataset files under [`../datasets/`](../datasets/) preserve task-facing fields such as `file`, `logic`, and verifier `results`. The adapter extracts stable metadata, source language, roles, and goal labels where available, and stores a compact source excerpt in `cryp_ir.metadata` for provenance.

---

## 📤 Report Shape

Single run:

```json
{
  "mode": "run",
  "task": "generation",
  "result": {
    "scheme": "nonce_key_exchange",
    "target": "spdl",
    "cryp_ir": {},
    "scaffold": {},
    "selected": {},
    "selected_score": 2.25,
    "candidates": []
  }
}
```

Batch run:

```json
{
  "mode": "batch",
  "task": "generation",
  "target": "spdl",
  "count": 5,
  "results": []
}
```

---

## 🔌 Extension Points

| Component | Default | Replace with |
| --- | --- | --- |
| Provider | `OfflineReferenceProvider` | API-backed LLM provider. |
| Verifier | `OfflineVerifierAdapter` | Scyther/Tamarin/ProVerif/etc. adapter. |
| Lowerer | `ReferenceLowerer` | Full target-language lowerer. |
| Repair | `Repairer` | Tool-specific repair policy. |
| Ranking | `Ranker` | Budget-aware ranking strategy. |

The JSON report schema stays fixed when components are replaced, which is the main reproducibility boundary for this reference code.
