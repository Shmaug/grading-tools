import os
import shutil
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

ignore = [
    ".git",
    "handouts",
    "__MACOSX"
]

names = [
    "*custom*.png"
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Canvas student submission comparison utility.')
    parser.add_argument('submissions_dir', help='Directory containing the student subfolders.')
    parser.add_argument('output_dir',      help='Directory containing the copied custom images.')
    parser.add_argument('--filter',        help="Additonal names to search for")
    args = parser.parse_args()

    # support multiple --filter inputs (list from argparse, repeated flags, or comma-separated)
    if args.filter:
        extra = []
        if isinstance(args.filter, str):
            extra = [s.strip() for s in args.filter.split(',') if s.strip()]
        else:
            for it in args.filter:
                if isinstance(it, str) and ',' in it:
                    extra.extend([s.strip() for s in it.split(',') if s.strip()])
                else:
                    extra.append(it)
        names.extend(extra)

    os.makedirs(args.output_dir, exist_ok=True)

    students = os.listdir(args.submissions_dir)

    maxlen = max([ len(s) for s in students ])
    missing = 0

    root = tk.Tk()
    root.withdraw()
    
    for student in students:
        student_dir = os.path.join(args.submissions_dir, student)
        found = None
        for name in names:
            for f in Path(student_dir).rglob(name):
                ignored = False
                for i in ignore:
                    if i in str(f):
                        ignored = True
                        break
                if not ignored:
                    found = f
                    break
            if found is not None:
                break

        if found is None:
            found = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")], initialdir=student_dir)
            if not os.path.exists(found):
                found = None

        if found is not None:
            shutil.copy(found, os.path.join(args.output_dir, student + ".png"))
            print(f"{student:<{maxlen}}  {os.path.relpath(found, student_dir)}")
        else:
            print(f"{student}")
            missing += 1
    
    print(f"Missing {missing}/{len(students)} custom images")