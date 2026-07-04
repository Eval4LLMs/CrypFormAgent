<h1 align="center">🏗️ Implementation Notes</h1>

<p align="center">
  <b>Architecture, Component Boundaries, Budgets, and Reproducibility Signals</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Core-CrypIR-blue">
  <img src="https://img.shields.io/badge/Targets-7%20Languages-success">
  <img src="https://img.shields.io/badge/Repair-Verifier%20Guided-orange">
  <img src="https://img.shields.io/badge/Ranking-Budgeted-purple">
</p>

> CrypFormAgent is implemented as a modular Python framework for verifier-grounded cryptographic scheme formalization. The public repository exposes this architecture through the executable reference implementation in [`../code/`](../code/), together with released datasets, dashboard traces, and aggregate result files.

---

## 🔁 Architecture Flow

```text
task normalization
      |
      v
CrypIR construction
      |
      v
semantic consistency checking
      |
      v
target-language lowering
      |
      v
candidate generation -> verifier execution -> consistency review
      |
      v
typed repair -> budgeted ranking
```

---

## 🧾 Task Normalization

The front end normalizes each task into a task-specific schema:

| Task | Normalized input |
| --- | --- |
| Generation | Logic description and target language. |
| Completion | Partial or masked formal artifact. |
| Correction | Faulty formal artifact plus verifier feedback when available. |
| Interpretation | Source formal artifact to explain. |
| Transformation | Source artifact, source language, and target language. |

CrypIR construction combines lightweight parsing and model-assisted semantic extraction. CrypIR records roles, typed terms, message flows, adversary assumptions, security goals, source/target language identifiers, and task metadata.

Semantic checks validate declaration coverage, term provenance, freshness, message-flow coherence, goal support, secrecy exposure, and source-target preservation when applicable.

---

## 🧰 Lowerers and Verifier Adapters

The research system contains deterministic lowerers for seven formal languages:

| Language | Tool |
| --- | --- |
| SPDL | Scyther |
| SPTHY | Tamarin |
| PV | ProVerif |
| HLPSL | AVISPA |
| Maude | Maude-NPA |
| EC | EasyCrypt |
| CV | CryptoVerif |

Each lowerer projects CrypIR into a target-language scaffold that fixes stable structure such as roles, declarations, messages, claims, queries, lemmas, environment blocks, and proof obligations. The lowerer does not replace the backbone model; it constrains the model to complete target-language details from a semantically grounded starting point.

Verifier adapters normalize tool outputs into shared states such as `safe`, `unsafe`, `compile_error`, `timeout`, and `unknown`. When available, adapters extract structured diagnostics for missing declarations, syntax/type errors, unsupported goals, guardedness failures, failed obligations, attack traces, and verdict inconsistencies.

---

## ⚙️ Backbones, Budgets, and Repair

The framework is backbone-agnostic. The same orchestration code can wrap different LLMs while keeping CrypIR checks, lowerers, verifier feedback parsing, typed repair, review, and ranking fixed.

Unless otherwise stated in the paper, each CrypFormAgent run uses:

| Parameter | Default |
| --- | ---: |
| Candidate budget `K` | 3 |
| Repair budget `R` | 2 |

Typed repair routes normalized verifier feedback to local structural repair or constrained model-assisted revision. Structural repair handles local issues such as missing declarations, duplicate definitions, or omitted goals when the fix can be derived from CrypIR. Non-local semantic and verdict-level inconsistencies are repaired under CrypIR constraints and then rechecked.

---

## 📜 Logging and Reproducibility

The evaluation records:

| Signal | Purpose |
| --- | --- |
| CrypIR drafts and normalized CrypIR objects | Inspect semantic recovery. |
| Consistency warnings | Identify unsupported or drifted semantics. |
| Lowerer outputs | Inspect target-language anchors. |
| Raw and repaired candidates | Compare model output and repair effect. |
| Verifier outputs and parsed feedback | Reproduce analyzability/correctness decisions. |
| Review signals and final rankings | Reconstruct candidate selection. |

Labels and reference answers are used only by evaluation scripts after a final artifact is selected. The implementation described in the paper contains approximately 18,620 lines of Python and 200 lines of YAML configuration, excluding datasets, generated outputs, logs, tests, temporary files, and external verifier installations.
