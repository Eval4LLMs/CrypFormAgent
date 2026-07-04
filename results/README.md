<h1 align="center">📈 Results and Model Outputs</h1>

<p align="center">
  <b>Aggregate Metrics, Released Model Outputs, and Ablation Records</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Aggregate%20Systems-16-blue">
  <img src="https://img.shields.io/badge/Output%20Families-7-success">
  <img src="https://img.shields.io/badge/Output%20Files-252-orange">
  <img src="https://img.shields.io/badge/Tasks-6-purple">
</p>

> This directory stores the result data used by the paper and dashboard. It  separates aggregate metric tables from released model-output traces so that readers can inspect both summary performance and representative generated artifacts.

---

## 🔗 Quick Map

| Path | Purpose |
| --- | --- |
| `model_language_task_results.json` | Aggregated counts by system, language, and task. |
| `model_outputs/` | Released per-model output JSON files organized by task and language. |

---

## 📊 Aggregate Result File

`model_language_task_results.json` is a nested JSON object:

```text
system -> language -> task -> metric counters
```

It includes direct baselines, CrypFormAgent variants, and ablation settings. The language layer includes the seven formal languages plus `overall` summary entries when available.

| Field | Meaning |
| --- | --- |
| `len` | Number of benchmark instances in the slice. |
| `num_generates` | Number of non-empty generated outputs. |
| `num_analysis` | Number of analyzable outputs accepted by the evaluation pipeline. |
| `tp`, `tn`, `fp`, `fn` | Verdict-level confusion-count components after normalization. |
| `num_timeout` | Number of runs that timed out. |

Task keys include:

| Task key | Meaning |
| --- | --- |
| `generation` | Logic description to formal artifact. |
| `completion` | Masked artifact completion. |
| `correction_error` | Syntax/error repair. |
| `correction_false` | False-verdict semantic repair. |
| `interpretation` | Formal artifact interpretation. |
| `transformation` | Cross-language formalization. |

---

## 🤖 Released Model Outputs

`model_outputs/` stores released outputs for seven direct model families:

| Model folder |
| --- |
| `claude-3-5-sonnet-coder` |
| `deepseek-coder` |
| `gemini-2.5-pro-exp-03-25` |
| `glm-4-airx` |
| `gpt-4o` |
| `grok-3-re` |
| `llama4-maverick-instruct-basic` |

The general layout is:

```text
model_outputs/
└─ <model>/
   ├─ generation/<language>/<language>_files_all.json
   ├─ completion/<language>/<language>_files_all.json
   ├─ interpretation/<language>/<language>_files_all.json
   ├─ correction/<language>/(error|false)/<language>_files_all.json
   └─ translation/files_all.json
```

These files preserve model-side outputs and evaluation-facing bookkeeping used to build dashboard traces and aggregate metrics.

---

## 🧭 How to Inspect

Pretty-print the aggregate metrics:

```bash
python3 -m json.tool model_language_task_results.json | less
```

List released output files for one model:

```bash
find model_outputs/gpt-4o -type f | sort
```

Open a translation output bundle:

```bash
python3 -m json.tool model_outputs/gpt-4o/translation/files_all.json | less
```

---

## 📌 Notes

- The aggregate file is the source for paper-level and dashboard-level summary statistics.
- The output bundles are released traces, not rerun scripts. Re-execution of external verifiers or LLM APIs requires tool-specific infrastructure outside this offline artifact.
- For metric robustness checks, see [`../scoring/`](../scoring/).
- For task data and property coverage, see [`../datasets/`](../datasets/).
