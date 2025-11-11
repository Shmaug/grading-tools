import os
import argparse
import cv2
import numpy as np
import csv
import re
from pathlib import Path

def parse_filename(name):
    """
    Returns (hw, problem, img).
    Assumes ref files are formatted as "hw_<homework>_<problem>_<img>" e.g., hw_2_1_3 for homework 2, problem 1, image 3.
    """
    s = name.split('_')
    return int(s[1]), int(s[2]), s[3]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Canvas student submission comparison utility.')
    parser.add_argument('ref_dir',         help='Directory containing the reference images.')
    parser.add_argument('submissions_dir', help='Directory containing the images to compare, i.e., the student subfolder.')
    parser.add_argument('reference_csv',   help="CSV file containing the student names. The columns are assumed to be in order of problem numbers.")
    parser.add_argument('output_csv',      help="Output CSV file containing the calculated grades.")
    parser.add_argument('--tolerance',     required=False, help='Pixel difference tolerance to assign full credit.', default=1)
    args = parser.parse_args()

    for p in [ args.ref_dir, args.submissions_dir, args.reference_csv ]:
        if not os.path.exists(p):
            print(f"Error: '{p}' does not exist.")
            exit(1)

    students        = sorted(os.listdir(args.submissions_dir))
    ref_image_names = sorted(os.listdir(args.ref_dir))

    # Load reference images, count the number of problems
    ref_images = {}

    # assumes problem numbers start at 1
    num_problems = 0
    for ref_img_name in ref_image_names:
        hw, problem, img = parse_filename(ref_img_name)
        num_problems = max(num_problems, problem)
        ref_images[ref_img_name] = cv2.imread(os.path.join(args.ref_dir, ref_img_name), cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)

    # Parse the reference CSV to determine where each student's grade will be written
    csv_rows = []
    max_scores = [0] * num_problems
    student_row_indices = {}
    with open(args.reference_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            csv_rows.append(row)
            if len(csv_rows) == 1:
                for problem in range(1,1+num_problems):
                    # Assumes the max score is in the header as '#pts'
                    header = row[problem]
                    m = re.search(r'(\d+)\s*#?\s*pts', header, flags=re.IGNORECASE)
                    if m:
                        max_scores[problem-1] = int(m.group(1))
                    else:
                        m2 = re.search(r'(\d+)', header)
                        max_scores[problem-1] = int(m2.group(1)) if m2 else 1
            else:
                lastname,firstname = row[0].split(", ")
                student = lastname + firstname
                student = student.replace("-","").replace(" ","").lower()
                student_row_indices[student] = len(csv_rows)-1
    
    # Calculate the grades
    for student in students:
        if student not in student_row_indices:
            print(f"Unknown student: '{student}'")
            continue

        problem_errors = [[] for _ in range(num_problems)]
        missing = []
        complete_submission = True
        
        for ref_img_name in ref_image_names:
            hw, problem, img = parse_filename(ref_img_name)
            found_files = []
            for f in Path(os.path.join(args.submissions_dir, student)).rglob(ref_img_name):
                found_files += [f]
            if len(found_files) == 0:
                complete_submission = False
                missing.append(ref_img_name)
                continue
            if len(found_files) > 1:
                complete_submission = False
                print(f"{student}: Found multiple submissions for {ref_img_name}: {found_files}")
                continue

            submitted_img = cv2.imread(found_files[0], cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
            if ref_images[ref_img_name].shape != submitted_img.shape:
                complete_submission = False
                print(f"{student}: Image size mismatch for {ref_img_name}: {ref_images[ref_img_name].shape} != {submitted_img.shape}")
                continue

            img_max_error = np.max(abs(ref_images[ref_img_name].astype(np.int16) - submitted_img.astype(np.int16)))
            problem_errors[problem-1].append(img_max_error)
        
        if complete_submission:
            for problem in range(1,1+num_problems):
                if len(problem_errors[problem-1]) > 0 and max(problem_errors[problem-1]) < args.tolerance:
                    csv_rows[student_row_indices[student]][problem] = str(max_scores[problem - 1])
        elif len(missing) > 0:
            print(f"{student}: Missing: {missing}")
    
    with open(args.output_csv, "w") as csvfile:
        writer = csv.writer(csvfile, lineterminator="\n")
        writer.writerows(csv_rows)