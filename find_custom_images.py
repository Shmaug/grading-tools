import os
import shutil
import argparse
from pathlib import Path

ignore = [
    ".git",
    "handouts",
    "__MACOSX"
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Canvas student submission comparison utility.')
    parser.add_argument('submissions_dir', help='Directory containing the student subfolders.')
    parser.add_argument('output_dir', help='Directory containing the copied custom images.')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    students = os.listdir(args.submissions_dir)

    maxlen = max([ len(s) for s in students ])
    missing = 0
    
    for student in students:
        student_dir = os.path.join(args.submissions_dir, student)
        found = None
        for f in Path(student_dir).rglob("*1_7*.png"):
            ignored = False
            for i in ignore:
                if i in str(f):
                    ignored = True
                    break
            if not ignored:
                found = f
                break

        if found is not None:
            shutil.copy(found, os.path.join(args.output_dir, student + ".png"))
            print(f"{student:<{maxlen}}  {os.path.relpath(found, student_dir)}")
        else:
            print(f"{student}")
            missing += 1
    
    print(f"Missing {missing}/{len(students)} custom images")