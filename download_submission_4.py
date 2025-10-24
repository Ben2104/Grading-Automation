#!/usr/bin/env python3
import os
import pathlib
import sys
import time
import codepost
import dotenv
dotenv.load_dotenv()
# --- CONFIG: update these if needed ---

COURSE_ID = 5290 # FIXME depends on your course
ASSIGNMENT_ID = 36143 # FIXME depends on your assignment
OUTDIR = "./downloads"   # base folder for saving files
TARGET_FILENAME = "pa4.py"  # Only download this file 
# --------------------------------------
def get_api_key():
    key = os.getenv("CODEPOST_API_KEY", "").strip()
    if not key:
        sys.exit("Missing API key. Set CODEPOST_API_KEY or edit the script to hardcode it.")
    return key

def safe_folder_name(name: str) -> str:
    # make safe-ish folder names on all OSes
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip()

def main():
    codepost.configure_api_key(get_api_key())

    # 1) Find course
    course = codepost.course.retrieve(COURSE_ID)
    course_dir = safe_folder_name(f"{course.name} ({course.period})")

    # 2) Find assignment (by ID is most reliable)
    assignment = codepost.assignment.retrieve(ASSIGNMENT_ID)
    assignment_dir = safe_folder_name(assignment.name)

    base = pathlib.Path(OUTDIR) / course_dir / assignment_dir
    base.mkdir(parents=True, exist_ok=True)

    print(f"Downloading submissions for:\n  Course: {course.name} ({course.period}) [ID {course.id}]\n"
          f"  Assignment: {assignment.name} [ID {assignment.id}]\n  -> {base.resolve()}\n")
    print(f"  Filtering for: {TARGET_FILENAME}\n")

    # 3) Get all submissions
    submissions = None
    # Preferred SDK method:
    try:
        submissions = assignment.list_submissions()
    except AttributeError:
        # Fallback if SDK version differs
        try:
            submissions = list(getattr(assignment, "submissions", []))
        except Exception as e:
            sys.exit(f"Could not enumerate submissions: {e}")

    total_files = 0
    skipped_students = []
    
    for sub in submissions:
        # Build a stable folder name per submission (handles partners/groups)
        students = getattr(sub, "students", []) or []
        if not students:
            folder = f"submission_{sub.id}"
        else:
            folder = ",".join(sorted(students))
        sub_dir = base / safe_folder_name(folder)
        sub_dir.mkdir(parents=True, exist_ok=True)

        # Iterate files in the submission
        files = getattr(sub, "files", []) or []
        found_target = False
        
        for f in files:
            # Some SDK objects are lazy; refresh if supported
            try:
                f.refresh()
            except Exception:
                pass

            name = getattr(f, "name", f"file_{getattr(f,'id','unknown')}")
            
            # Only process the target file
            if name != TARGET_FILENAME:
                continue
            
            found_target = True
            rel_path = getattr(f, "path", None)  # optional subdirectory
            code = getattr(f, "code", None)

            # Recreate any folder structure the student had
            out_dir = sub_dir / safe_folder_name(rel_path) if rel_path else sub_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / name

            # Files in CodePost are text; write as UTF-8, fall back if needed
            if code is None:
                print(f"  [skip] {folder}/{name} (no text content)")
                continue

            try:
                with open(out_file, "w", encoding="utf-8", newline="") as fh:
                    fh.write(code)
                total_files += 1
                print(f"  ✓ {folder}/{name}")
            except UnicodeEncodeError:
                # Fallback encoding
                with open(out_file, "w", encoding="utf-8", errors="replace", newline="") as fh:
                    fh.write(code)
                total_files += 1
                print(f"  ✓ {folder}/{name} (encoding fallback)")

            # Optional: light throttling to be polite to the API on very large classes
            # time.sleep(0.02)
        
        if not found_target:
            skipped_students.append(folder)
            print(f"  ✗ {folder} (no {TARGET_FILENAME} found)")

    print(f"\n✅ Done. Saved {total_files} {TARGET_FILENAME} file(s) under: {base.resolve()}")
    
    if skipped_students:
        print(f"\n⚠️  {len(skipped_students)} submission(s) missing {TARGET_FILENAME}:")
        for student in skipped_students[:10]:  # Show first 10
            print(f"    - {student}")
        if len(skipped_students) > 10:
            print(f"    ... and {len(skipped_students) - 10} more")

if __name__ == "__main__":
    main()