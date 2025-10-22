#!/usr/bin/env python3
"""
grade_pa3_code.py

Runs Python-based tests that call pa3.* functions:
- Each test file defines TestCase() -> (bool, str)
- We run each test in a subprocess so timeouts/crashes don't kill the harness
- We inject the student's pa3.py so `import pa3` inside the test refers to that student's code
- Tests import util from tests/pa3/code_tests directory
- We add tests/pa3/support/ to sys.path so `import pa3sol` works

Outputs:
  - pa3_code_results.csv  (per-test details)
  - pa3_code_summary.csv  (per-student totals)

Usage:
  python grade_pa3_code.py
  # or override:
  python grade_pa3_code.py --submissions-dir "downloads/.../Programming Assignment #3" \
                           --tests-dir tests/pa3/code_tests \
                           --support-dir tests/pa3/support \
                           --results-csv pa3_code_results.csv \
                           --summary-csv pa3_code_summary.csv \
                           --timeout 6
"""

import argparse
import csv
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from typing import List, Dict
from datetime import datetime

# ---------- Defaults tailored to your project ----------
DEFAULT_SUBMISSIONS = "downloads/CECS 229 SEC 02 4829 (Fall 2025)/Programming Assignment #3"
DEFAULT_TESTS_DIR = "tests/pa3/code_tests"
DEFAULT_SUPPORT_DIR = "tests/pa3/code_tests"
DEFAULT_RESULTS_CSV = "pa3_code_results.csv"
DEFAULT_SUMMARY_CSV = "pa3_code_summary.csv"
DEFAULT_LOG_FILE = "pa3_grading_log.txt"
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
    # args: student_pa3_path, tests_dir, support_dir, test_file_path, seed
    if len(sys.argv) < 6:
        print(json.dumps({"ok": False, "message": "bad_args", "error": "Expected 5 arguments"}))
        return
    
    student_pa3_path = sys.argv[1]
    tests_dir = sys.argv[2]
    support_dir = sys.argv[3]
    test_file_path = sys.argv[4]
    seed = int(sys.argv[5])

    # Verify paths exist
    if not os.path.exists(student_pa3_path):
        print(json.dumps({"ok": False, "message": "Student pa3.py not found", "error": f"Path does not exist: {student_pa3_path}"}))
        return
    
    if not os.path.exists(test_file_path):
        print(json.dumps({"ok": False, "message": "Test file not found", "error": f"Path does not exist: {test_file_path}"}))
        return

    # Priority for imports:
    # 1. tests_dir (for util.py used by tests)
    # 2. support_dir (for pa3sol.py)
    if tests_dir and os.path.exists(tests_dir):
        sys.path.insert(0, tests_dir)
    
    if support_dir and os.path.exists(support_dir):
        sys.path.insert(0, support_dir)

    # Load student's pa3.py as module "pa3"
    try:
        pa3_mod = load_module_from_path("pa3", student_pa3_path)
    except Exception as e:
        error_msg = traceback.format_exc()
        print(json.dumps({
            "ok": False, 
            "message": "Failed to load student's pa3.py", 
            "error": error_msg
        }))
        return

    # Load the test module (it will import pa3, pa3sol, util from sys.path)
    try:
        test_mod = load_module_from_path(Path(test_file_path).stem, test_file_path)
    except Exception as e:
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
    except Exception as e:
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
        self.log(f"=== PA3 Grading Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    def log(self, message: str):
        """Log message to both console and file."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.log_file.write(log_message + '\n')
        self.log_file.flush()
    
    def log_traceback(self, student: str, test_name: str, message: str, error: str = "", stderr: str = ""):
        """Log detailed traceback information for failed tests."""
        self.log(f"  ✗ {test_name} FAILED for {student}")
        self.log(f"    MESSAGE: {message[:300]}")
        if error:
            self.log(f"    ERROR TRACEBACK:")
            # Split error into lines and log each line with proper indentation
            for line in error.split('\n')[:20]:  # Limit to first 20 lines
                if line.strip():
                    self.log(f"      {line}")
        if stderr:
            self.log(f"    STDERR:")
            for line in stderr.split('\n')[:10]:  # Limit to first 10 lines
                if line.strip():
                    self.log(f"      {line}")
    
    def close(self):
        """Close the log file."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        self.log(f"=== PA3 Grading Completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Duration: {duration}) ===")
        self.log_file.close()

def find_test_files(tests_dir: pathlib.Path) -> List[pathlib.Path]:
    return sorted([p for p in tests_dir.iterdir() if p.is_file() and p.name.startswith("test_") and p.suffix==".py"])

def main():
    ap = argparse.ArgumentParser(description="Run code-based PA3 tests (TestCase() in each test_*.py).")
    ap.add_argument("--submissions-dir", default=DEFAULT_SUBMISSIONS)
    ap.add_argument("--tests-dir", default=DEFAULT_TESTS_DIR)
    ap.add_argument("--support-dir", default=DEFAULT_SUPPORT_DIR)
    ap.add_argument("--results-csv", default=DEFAULT_RESULTS_CSV)
    ap.add_argument("--summary-csv", default=DEFAULT_SUMMARY_CSV)
    ap.add_argument("--log-file", default=DEFAULT_LOG_FILE)
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    ap.add_argument("--python-bin", default=sys.executable)
    args = ap.parse_args()

    submissions_dir = pathlib.Path(args.submissions_dir)
    tests_dir = pathlib.Path(args.tests_dir)
    support_dir = pathlib.Path(args.support_dir)
    results_csv = pathlib.Path(args.results_csv)
    summary_csv = pathlib.Path(args.summary_csv)
    log_file = pathlib.Path(args.log_file)
    
    # Initialize logger
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
        logger.log(f"WARN: Support dir not found: {support_dir.resolve()} (tests that import pa3sol may fail)")

    tests = find_test_files(tests_dir)
    if not tests:
        logger.log(f"ERROR: No test_*.py found in {tests_dir.resolve()}")
        logger.close()
        raise SystemExit(f"No test_*.py found in {tests_dir.resolve()}")

    logger.log(f"Found {len(tests)} test(s): {[t.name for t in tests]}")

    results_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_csv.parent.mkdir(parents=True, exist_ok=True)

    # Write the runner to a temp file for subprocess isolation
    with tempfile.TemporaryDirectory() as tmpd:
        runner_path = pathlib.Path(tmpd) / "runner.py"
        runner_path.write_text(RUNNER_CODE, encoding="utf-8")

        # Aggregates
        summary: Dict[str, Dict[str, int]] = {}

        with open(results_csv, "w", newline="", encoding="utf-8") as rf:
            rw = csv.writer(rf)
            rw.writerow(["student_email(s)", "test_file", "passed", "message"])

            for student_dir in sorted([p for p in submissions_dir.iterdir() if p.is_dir()]):
                student = student_dir.name
                summary.setdefault(student, {"total": 0, "passed": 0, "failed": 0, "missing_pa3": 0})

                # Locate student's pa3.py
                pa3_path = None
                direct = student_dir / "pa3.py"
                if direct.exists():
                    pa3_path = direct
                else:
                    for root, dirs, files in os.walk(student_dir):
                        if any(tag in root for tag in (".venv", "venv", "__pycache__")):
                            continue
                        if "pa3.py" in files:
                            pa3_path = pathlib.Path(root) / "pa3.py"
                            break

                if not pa3_path:
                    for t in tests:
                        rw.writerow([student, t.name, 0, "pa3.py not found"])
                        summary[student]["total"] += 1
                        summary[student]["failed"] += 1
                    summary[student]["missing_pa3"] = 1
                    logger.log(f"SKIP: {student}: pa3.py not found")
                    continue

                logger.log(f"RUN: {student} -> {pa3_path.relative_to(student_dir)}")

                # Run each test in its own subprocess with a deterministic seed
                for idx, tfile in enumerate(tests):
                    # Special logging for RSA tests (test cases 3 and 4)
                    if tfile.name in ['test_3_1.py', 'test_3_2.py', 'test_4_1.py', 'test_4_2.py']:
                        logger.log(f"    Running RSA test: {tfile.name}")
                    seed = 1337 + idx  # stable seed per test index
                    cmd = [
                        args.python_bin,
                        str(runner_path),
                        str(pa3_path.resolve()),
                        str(tests_dir.resolve()),  # Pass tests dir for util.py
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
                        
                        # parse JSON
                        data = {}
                        try:
                            data = json.loads(out) if out else {}
                        except json.JSONDecodeError:
                            data = {"ok": False, "message": "Invalid JSON output", "error": f"STDOUT: {out[:500]}\nSTDERR: {err[:500]}"}

                        ok = bool(data.get("ok", False))
                        message = data.get("message", "")
                        error = data.get("error", "")

                        # Combine message and error for display
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
                            logger.log(f"  ✓ {tfile.name}")
                        else:
                            summary[student]["failed"] += 1
                            # Enhanced logging for test cases 3 and 4 (RSA tests)
                            if tfile.name in ['test_3_1.py', 'test_3_2.py', 'test_4_1.py', 'test_4_2.py']:
                                logger.log_traceback(student, tfile.name, message, error, err)
                            else:
                                logger.log(f"  ✗ {tfile.name}: {message[:100]}")

                    except subprocess.TimeoutExpired:
                        rw.writerow([student, tfile.name, 0, f"Test timed out after {args.timeout} seconds"])
                        summary[student]["total"] += 1
                        summary[student]["failed"] += 1
                        logger.log(f"  ✗ {tfile.name}: TIMEOUT")

        # Write summary
        with open(summary_csv, "w", newline="", encoding="utf-8") as sf:
            sw = csv.writer(sf)
            sw.writerow(["student_email(s)", "total_tests", "passed", "failed", "percent_passed", "missing_pa3"])
            for student, s in sorted(summary.items()):
                total = s["total"]
                passed = s["passed"]
                failed = s["failed"]
                pct = (passed / total * 100.0) if total else 0.0
                sw.writerow([student, total, passed, failed, f"{pct:.2f}", s["missing_pa3"]])

        logger.log(f"✅ Results:  {results_csv.resolve()}")
        logger.log(f"✅ Summary:  {summary_csv.resolve()}")
        logger.log(f"✅ Log file: {log_file.resolve()}")
        
        # Close the logger
        logger.close()

if __name__ == "__main__":
    main()