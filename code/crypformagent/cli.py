"""Command-line interface for the CrypFormAgent reference artifact."""

import argparse

from .pipeline import ArtifactPipeline, load_records, write_json


def build_parser():
    parser = argparse.ArgumentParser(
        prog="python3 -m crypformagent",
        description="Run the offline CrypFormAgent reference pipeline",
    )
    parser.add_argument("command", nargs="?", choices=["run", "batch"], default="run")
    add_common_args(parser)
    parser.add_argument("--index", type=int, default=0, help="Record index when input is a JSON list")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of records to run in batch mode")
    return parser


def add_common_args(parser):
    parser.add_argument("--input", required=True, help="Path to CrypIR JSON or released dataset JSON")
    parser.add_argument("--target", default="spdl", help="Target language: spdl, spthy, pv, hlpsl, maude, ec, cv")
    parser.add_argument("--task", default="generation", help="Task label stored in the output report")
    parser.add_argument("--candidates", type=int, default=1, help="Number of offline candidates to generate")
    parser.add_argument("--output", help="Optional path for a JSON report")


def main():
    args = build_parser().parse_args()
    command = args.command or "run"
    pipeline = ArtifactPipeline(candidate_count=args.candidates)

    if command == "batch":
        records = load_records(args.input, target=args.target, task=args.task, limit=args.limit)
        results = [pipeline.run(record, args.target) for record in records]
        report = {
            "mode": "batch",
            "task": args.task,
            "target": args.target,
            "count": len(results),
            "results": [result.to_dict() for result in results],
        }
        print_batch_summary(results, args.target)
    else:
        records = load_records(args.input, target=args.target, task=args.task)
        if args.index < 0 or args.index >= len(records):
            raise SystemExit("record index {} outside 0..{}".format(args.index, len(records) - 1))
        result = pipeline.run(records[args.index], args.target)
        report = {"mode": "run", "task": args.task, "result": result.to_dict()}
        print_single_summary(result)

    if args.output:
        write_json(args.output, report)
        print("Report:", args.output)
    return 0


def print_single_summary(result):
    print("CrypFormAgent reference run")
    print("Input:", result.cryp_ir.summary())
    print("Target:", result.target)
    print("Verifier:", result.selected.verification.status if result.selected else "no-candidate")
    print("Score:", "{:.2f}".format(result.score))
    print("")
    print(result.selected.artifact if result.selected else "")


def print_batch_summary(results, target):
    analyzable = sum(1 for result in results if result.selected and result.selected.verification.analyzable)
    mean_score = sum(result.score for result in results) / float(len(results) or 1)
    print("CrypFormAgent reference batch")
    print("Target:", target)
    print("Records:", len(results))
    print("Analyzable:", analyzable)
    print("Mean score:", "{:.2f}".format(mean_score))


if __name__ == "__main__":
    raise SystemExit(main())
