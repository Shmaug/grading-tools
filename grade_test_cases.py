import os
import argparse
import csv
import re
import subprocess
import tqdm

def process_student(test_script):
    proc = subprocess.run([ "python", test_script ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        proc.check_returncode()
    except subprocess.CalledProcessError:
        pass
    except KeyboardInterrupt:
        return 0

    output = proc.stderr.decode('utf-8')
    num_tests = 0
    passed = 0
    for line in output.split('\n'):
        if 'Ran' in line and 'tests in' in line:
            match = re.search(r'Ran (\d+) tests', line)
            if match:
                num_tests = int(match.group(1))
            
        if 'OK' in line:
            passed = num_tests
        elif "FAILED" in line:
            match_failed = re.search(r'FAILED \(errors=(\d+)', line)
            if match_failed:
                failed = int(match_failed.group(1))
                passed = num_tests - failed
            else:
                print(f"{test_script}: Failed to extract error count")
    return passed / num_tests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Canvas student submission comparison utility.')
    parser.add_argument('projects_dir', help='Directory containing the student projects.')
    parser.add_argument('test_script',  help='Path to test script, relative to student project dir.')
    parser.add_argument('max_score',    type=float, help='Maximum score.')
    parser.add_argument('output_csv',   help="Output CSV file containing the calculated grades.")
    args = parser.parse_args()

    if not os.path.exists(args.projects_dir):
        print(f"Error: '{args.projects_dir}' does not exist.")
        exit(1)

    students = sorted(os.listdir(args.projects_dir))

    with open(args.output_csv, "w") as csvfile:
        writer = csv.writer(csvfile, lineterminator="\n")
        for student in tqdm.tqdm(students):
            script = os.path.join(args.projects_dir, student, args.test_script)
            if not os.path.exists(script):
                print(f"Error: '{script}' does not exist.")
                grade = 0
            else:
                grade = process_student(script)
            # print(f"{student}: {100*grade:.2f}")
            writer.writerow([ student, f"{args.max_score*grade:.2f}" ])
            csvfile.flush()