import argparse
import json
import sys
from .core import analyze_run, freeze_split, validate_run
from .demo import demo
from .analysis import import_meter, fit_service, evaluate_service, failure_budget
from .acquire import telemetry, completion_request
from .cap import cap_session


def main():
    parser = argparse.ArgumentParser(description="W6 handoff; default acquisition is dry-run")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("demo"); p.add_argument("output")
    p = sub.add_parser("validate"); p.add_argument("run"); p.add_argument("--purpose", choices=["descriptive", "w6-dc", "pcc"], default="descriptive")
    p = sub.add_parser("analyze"); p.add_argument("run")
    p = sub.add_parser("freeze-split"); p.add_argument("registry"); p.add_argument("output")
    p = sub.add_parser("import-meter"); p.add_argument("csv"); p.add_argument("spec"); p.add_argument("output")
    for command in ("fit-service", "evaluate-service"):
        p = sub.add_parser(command); p.add_argument("root"); p.add_argument("split")
        if command == "evaluate-service": p.add_argument("model")
        p.add_argument("output")
    p = sub.add_parser("budget"); p.add_argument("--alpha", type=float, default=.05); p.add_argument("--delta", type=float, default=.05); p.add_argument("--endpoints", type=int, default=1)
    for command in ("telemetry", "request", "cap-session"):
        p = sub.add_parser(command); p.add_argument("config"); p.add_argument("output")
        p.add_argument("--execute-power-control" if command == "cap-session" else "--execute", action="store_true")
    a = parser.parse_args()
    try:
        if a.command == "demo": result = demo(a.output)
        elif a.command == "validate":
            m, _, _ = validate_run(a.run, a.purpose)
            result = {"validation": "PASSED_DECLARED_DATA_CONTRACT", "evidence": m["evidence"], "purpose": a.purpose,
                      "physical_certification": False}
        elif a.command == "analyze": result = analyze_run(a.run)
        elif a.command == "freeze-split": result = freeze_split(a.registry, a.output)
        elif a.command == "import-meter": result = import_meter(a.csv, a.spec, a.output)
        elif a.command == "fit-service": result = fit_service(a.root, a.split, a.output)
        elif a.command == "evaluate-service": result = evaluate_service(a.root, a.split, a.model, a.output)
        elif a.command == "budget": result = failure_budget(a.alpha, a.delta, a.endpoints)
        elif a.command == "telemetry": result = telemetry(a.config, a.output, a.execute)
        elif a.command == "request": result = completion_request(a.config, a.output, a.execute)
        else: result = cap_session(a.config, a.output, a.execute_power_control)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        # Never include HTTP payloads, prompt content or credentials in error logs.
        print(json.dumps({"status": "FAILED_CLOSED", "error_class": type(exc).__name__, "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
