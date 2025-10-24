#!/usr/bin/env python3
"""
grade_pa4_code.py

Runs Python-based tests that call pa4.* functions:
- Each test file defines TestCase() -> (bool, str)
- We run each test in a subprocess so timeouts/crashes don't kill the harness
- We inject the student's pa4.py so `import pa4` inside the test refers to that student's code
- Tests import util from tests/pa4/codetests directory
- We add tests/pa4/codetests/ to sys.path so `import pa4sol` works

Outputs:
  - pa4_code_results.csv  (per-test details)
  - pa4_code_summary.csv  (per-student totals)

Usage:
  python grade_pa4_code.py
  # or override:
  python grade_pa4_code.py --submissions-dir "downloads/.../Programming Assignment #4" \
                           --tests-dir tests/pa4/codetests \
                           --support-dir tests/pa4/codetests \
                           --results-csv pa4_code_results.csv \
                           --summary-csv pa4_code_summary.csv \
                           --timeout 20
"""

import argparse
import csv
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Dict, List

# ---------- Defaults tailored to your project ----------
DEFAULT_SUBMISSIONS = "downloads/CECS 229 SEC 02 4829 (Fall 2025)/Programming Assignment #4"
DEFAULT_TESTS_DIR = "tests/pa4/codetests"
DEFAULT_SUPPORT_DIR = "tests/pa4/codetests"
DEFAULT_RESULTS_CSV = "pa4_code_results.csv"
DEFAULT_SUMMARY_CSV = "pa4_code_summary.csv"
DEFAULT_LOG_FILE = "pa4_grading_log.txt"
DEFAULT_TIMEOUT = 20.0
# -------------------------------------------------------

RUNNER_CODE = r"""
import importlib.util
import json
import os
import random
import sys
import traceback
from pathlib import Path

def load_module_from_path(module_name: str, file_path: str):
    '''Load a Python module from a file path.'''
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create spec for {module_name} from {file_path}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod  # Register before exec
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        raise ImportError(f"Error loading {module_name} from {file_path}: {str(e)}\n{traceback.format_exc()}")

def main():
    # args: student_pa4_path, tests_dir, support_dir, test_file_path, seed
    if len(sys.argv) < 6:
        print(json.dumps({"ok": False, "message": "bad_args", "error": "Expected 5 arguments"}))
        return

    student_pa4_path = sys.argv[1]
    tests_dir = sys.argv[2]
    support_dir = sys.argv[3]
    test_file_path = sys.argv[4]
    seed = int(sys.argv[5])

    # Verify paths exist
    if not os.path.exists(student_pa4_path):
        print(json.dumps({"ok": False, "message": "Student pa4.py not found", "error": f"Path does not exist: {student_pa4_path}"}))
        return

    if not os.path.exists(test_file_path):
        print(json.dumps({"ok": False, "message": "Test file not found", "error": f"Path does not exist: {test_file_path}"}))
        return

    # Priority for imports:
    # 1. tests_dir (for util.py used by tests)
    # 2. support_dir (for pa4sol.py)
    if tests_dir and os.path.exists(tests_dir):
        sys.path.insert(0, tests_dir)

    if support_dir and os.path.exists(support_dir):
        sys.path.insert(0, support_dir)

    # Load student's pa4.py as module "pa4"
    try:
        _ = load_module_from_path("pa4", student_pa4_path)
    except Exception:
        error_msg = traceback.format_exc()
        print(json.dumps({
            "ok": False,
            "message": "Failed to load student's pa4.py",
            "error": error_msg
        }))
        return

    # Load the test module (it will import pa4, pa4sol, util from sys.path)
    try:
        test_mod = load_module_from_path(Path(test_file_path).stem, test_file_path)
    except Exception:
        error_msg = traceback.format_exc()
        print(json.dumps({
            "ok": False,
            "message": "Failed to load test file",
            "error": error_msg
        }))
        return

    # Set deterministic random seed
    random.seed(seed)

    # Run the test
    try:
        if not hasattr(test_mod, "TestCase"):
            raise AttributeError("TestCase() function not found in test file")

        result, msg = test_mod.TestCase()
        ok = bool(result)
        msg = str(msg)
        print(json.dumps({"ok": ok, "message": msg}))
    except Exception:
        error_msg = traceback.format_exc()
        print(json.dumps({
            "ok": False,
            "message": "Exception during TestCase() execution",
            "error": error_msg
        }))

if __name__ == "__main__":
    main()
"""


class ConsoleLogger:
    """A logger that writes to both console and file."""
    def __init__(self, log_file_path: str):
        self.log_file = open(log_file_path, 'w', encoding='utf-8')
        self.start_time = datetime.now()
        self.log(f"=== PA4 Grading Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")

    def log(self, message: str):
        """Log message to both console and file."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.log_file.write(log_message + '\n')
        self.log_file.flush()

    def log_test_details(self, student: str, test_name: str, ok: bool, message: str, error: str = "", stderr: str = ""):
        """Log detailed test information."""
        status = "✓ PASSED" if ok else "✗ FAILED"
        self.log(f"  {status} - {test_name}")
        
        # Log the full test message (input, output, expected)
        if message:
            lines = message.split('\n')
            for line in lines[:50]:  # Show first 50 lines of message
                self.log(f"    │ {line}")
        
        # Log error details if present
        if not ok and error:
            self.log(f"    ├─ ERROR DETAILS:")
            error_lines = error.split('\n')
            for line in error_lines[:30]:  # Show first 30 lines of error
                if line.strip():
                    self.log(f"    │   {line}")
        
        # Log stderr if present
        if not ok and stderr:
            self.log(f"    ├─ STDERR:")
            stderr_lines = stderr.split('\n')
            for line in stderr_lines[:20]:  # Show first 20 lines of stderr
                if line.strip():
                    self.log(f"    │   {line}")
        
        self.log(f"    └─ End of {test_name}")

    def close(self):
        """Close the log file."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        self.log(f"=== PA4 Grading Completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Duration: {duration}) ===")
        self.log_file.close()


def find_test_files(tests_dir: pathlib.Path) -> List[pathlib.Path]:
    return sorted([p for p in tests_dir.iterdir() if p.is_file() and p.name.startswith("test_") and p.suffix == ".py"])


def main():
    ap = argparse.ArgumentParser(description="Run code-based PA4 tests (TestCase() in each test_*.py).")
    ap.add_argument("--submissions-dir", default=DEFAULT_SUBMISSIONS)
    ap.add_argument("--tests-dir", default=DEFAULT_TESTS_DIR)
    ap.add_argument("--support-dir", default=DEFAULT_SUPPORT_DIR)
    ap.add_argument("--results-csv", default=DEFAULT_RESULTS_CSV)
    ap.add_argument("--summary-csv", default=DEFAULT_SUMMARY_CSV)
    ap.add_argument("--log-file", default=DEFAULT_LOG_FILE)
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    ap.add_argument("--python-bin", default=sys.executable)
    ap.add_argument("--verbose", action="store_true", help="Show detailed test output in console")
    args = ap.parse_args()

    submissions_dir = pathlib.Path(args.submissions_dir)
    tests_dir = pathlib.Path(args.tests_dir)
    support_dir = pathlib.Path(args.support_dir)
    results_csv = pathlib.Path(args.results_csv)
    summary_csv = pathlib.Path(args.summary_csv)
    log_file = pathlib.Path(args.log_file)

    logger = ConsoleLogger(str(log_file))

    if not submissions_dir.exists():
        logger.log(f"ERROR: Submissions directory not found: {submissions_dir.resolve()}")
        logger.close()
        raise SystemExit(f"Submissions directory not found: {submissions_dir.resolve()}")
    if not tests_dir.exists():
        logger.log(f"ERROR: Tests directory not found: {tests_dir.resolve()}")
        logger.close()
        raise SystemExit(f"Tests directory not found: {tests_dir.resolve()}")
    if not support_dir.exists():
        logger.log(f"WARN: Support dir not found: {support_dir.resolve()} (tests that import pa4sol may fail)")

    tests = find_test_files(tests_dir)
    if not tests:
        logger.log(f"ERROR: No test_*.py found in {tests_dir.resolve()}")
        logger.close()
        raise SystemExit(f"No test_*.py found in {tests_dir.resolve()}")

    logger.log(f"Found {len(tests)} test(s): {[t.name for t in tests]}")
    logger.log(f"Submissions directory: {submissions_dir.resolve()}")
    logger.log(f"Tests directory: {tests_dir.resolve()}")
    logger.log(f"Timeout: {args.timeout}s")
    logger.log("")

    results_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_csv.parent.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, Dict[str, int]] = {}

    with tempfile.TemporaryDirectory() as tmpd:
        runner_path = pathlib.Path(tmpd) / "runner.py"
        runner_path.write_text(RUNNER_CODE, encoding="utf-8")

        with open(results_csv, "w", newline="", encoding="utf-8") as rf:
            rw = csv.writer(rf)
            rw.writerow(["student_email(s)", "test_file", "passed", "message"])

            student_dirs = sorted([p for p in submissions_dir.iterdir() if p.is_dir()])
            logger.log(f"Processing {len(student_dirs)} student submission(s)...")
            logger.log("=" * 80)

            for student_idx, student_dir in enumerate(student_dirs, 1):
                student = student_dir.name
                summary.setdefault(student, {"total": 0, "passed": 0, "failed": 0, "missing_pa4": 0})

                logger.log(f"\n[{student_idx}/{len(student_dirs)}] Processing: {student}")
                logger.log("-" * 80)

                pa4_path = None
                direct = student_dir / "pa4.py"
                if direct.exists():
                    pa4_path = direct
                else:
                    for root, dirs, files in os.walk(student_dir):
                        if any(tag in root for tag in (".venv", "venv", "__pycache__")):
                            continue
                        if "pa4.py" in files:
                            pa4_path = pathlib.Path(root) / "pa4.py"
                            break

                if not pa4_path:
                    for t in tests:
                        rw.writerow([student, t.name, 0, "pa4.py not found"])
                        summary[student]["total"] += 1
                        summary[student]["failed"] += 1
                    summary[student]["missing_pa4"] = 1
                    logger.log(f"  ⚠️  SKIPPED: pa4.py not found")
                    continue

                logger.log(f"  📁 Found: {pa4_path.relative_to(student_dir)}")

                for idx, tfile in enumerate(tests, 1):
                    seed = 1337 + idx
                    cmd = [
                        args.python_bin,
                        str(runner_path),
                        str(pa4_path.resolve()),
                        str(tests_dir.resolve()),
                        str(support_dir.resolve() if support_dir.exists() else ""),
                        str(tfile.resolve()),
                        str(seed),
                    ]
                    try:
                        proc = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=args.timeout,
                        )
                        out = (proc.stdout or "").strip()
                        err = (proc.stderr or "").strip()

                        try:
                            data = json.loads(out) if out else {}
                        except json.JSONDecodeError:
                            data = {"ok": False, "message": "Invalid JSON output", "error": f"STDOUT: {out[:500]}\nSTDERR: {err[:500]}"}

                        ok = bool(data.get("ok", False))
                        message = data.get("message", "")
                        error = data.get("error", "")

                        full_message = message
                        if error:
                            full_message += f"\n\nERROR:\n{error}"
                        if proc.returncode != 0:
                            full_message += f"\n\n(subprocess exit code: {proc.returncode})"
                        if err and not error:
                            full_message += f"\n\nSTDERR:\n{err}"

                        rw.writerow([student, tfile.name, int(ok), full_message])
                        summary[student]["total"] += 1
                        if ok:
                            summary[student]["passed"] += 1
                        else:
                            summary[student]["failed"] += 1

                        # Log detailed test information
                        logger.log_test_details(student, tfile.name, ok, message, error, err)

                    except subprocess.TimeoutExpired:
                        timeout_msg = f"Test timed out after {args.timeout} seconds"
                        rw.writerow([student, tfile.name, 0, timeout_msg])
                        summary[student]["total"] += 1
                        summary[student]["failed"] += 1
                        logger.log(f"  ✗ FAILED - {tfile.name}")
                        logger.log(f"    │ {timeout_msg}")
                        logger.log(f"    └─ End of {tfile.name}")

                # Log student summary
                s = summary[student]
                logger.log(f"\n  📊 Student Summary: {s['passed']}/{s['total']} passed ({s['passed']/s['total']*100:.1f}%)")

    # Write summary CSV
    with open(summary_csv, "w", newline="", encoding="utf-8") as sf:
        sw = csv.writer(sf)
        sw.writerow(["student_email(s)", "total_tests", "passed", "failed", "percent_passed", "missing_pa4"])
        for student, s in sorted(summary.items()):
            total = s["total"]
            passed = s["passed"]
            failed = s["failed"]
            pct = (passed / total * 100.0) if total else 0.0
            sw.writerow([student, total, passed, failed, f"{pct:.2f}", s["missing_pa4"]])

    logger.log("\n" + "=" * 80)
    logger.log(f"✅ Results:  {results_csv.resolve()}")
    logger.log(f"✅ Summary:  {summary_csv.resolve()}")
    logger.log(f"✅ Log file: {log_file.resolve()}")
    logger.close()


if __name__ == "__main__":
    main()