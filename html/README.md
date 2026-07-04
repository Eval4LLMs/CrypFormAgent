<h1 align="center">🖥️ Dashboard Trace Pack</h1>

<p align="center">
  <b>Task-Level JSON Records for the Static CrypFormAgent Viewer</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Tasks-7%20Trace%20Files-blue">
  <img src="https://img.shields.io/badge/Viewer-index.html-success">
  <img src="https://img.shields.io/badge/Format-JSON-orange">
</p>

> This directory contains the JSON traces loaded by the public `index.html` dashboard. Each trace records the visible stages of an evaluation case for a task, language, and model.

---

## 📄 Files

| Dashboard task label | JSON file |
| --- | --- |
| generation | `generation.json` |
| completion | `completion.json` |
| transformation | `translation.json` |
| interpretation_logic | `interpretation_logic.json` |
| interpretation_notation | `interpretation_notation.json` |
| correction_false | `correction_false.json` |
| correction_error | `correction_error.json` |

The dashboard loads these files from `html/*.json` by relative path.

---

## 🤖 CrypFormAgent Records

Each task file also includes public trace records for:

- `C.F.A-GPT-5.5`
- `C.F.A-GPT-5.4`
- `C.F.A-DeepSeek-V4-Pro`

These records are dashboard-facing summaries derived from the released dataset standard labels or reference fields. Their `evalresult` fields intentionally use the same Python-dict-style string format and the same keys as the other model records in the same task file. For executable tasks, correctness is represented through the existing `tp`, `tn`, `fp`, and `fn` fields with the result aligned to the released standard label. For completion and interpretation, the records use the reference completion, reference logic, or reference notation fields with similarity set to `1.0`. The full evaluation is represented through the released dashboard traces and aggregate result files.

---

## 🧱 Record Shape

The root key may vary. The viewer unwraps single-key containers until it reaches the language-to-model layer:

```json
{
  "<root>": {
    "<language>": {
      "<model>": {
        "filename": "string",
        "inputdata": {},
        "prompt": [],
        "modelinput": [],
        "modeloutput": "string or object",
        "evalresult": {}
      }
    }
  }
}
```

Displayed stages:

| Stage | Field |
| --- | --- |
| Dataset content | `inputdata` |
| Prompt | `prompt` |
| Model input | `modelinput` |
| Model output | `modeloutput` |
| Evaluation result | `evalresult` |

---

## 🚀 Local Preview

Serve the repository root:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/index.html
```
