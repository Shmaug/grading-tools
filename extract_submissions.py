import os
import zipfile
import argparse
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Canvas student submission extraction utility.')
    parser.add_argument('submissions_zip', help='Zipped submissions as downloaded from Canvas')
    parser.add_argument('output_folder',   help='Output folder. Student subfolders will be placed here.')
    parser.add_argument('--verbose', action='store_true', help='Print the names of extracted files.')
    args = parser.parse_args()

    input_zip     = args.submissions_zip
    output_folder = args.output_folder

    if not os.path.exists(input_zip):
        print(f"Error: '{input_zip}' does not exist")
        exit(1)

    os.makedirs(output_folder, exist_ok=True)

    student_ids = {}

    try:
        with zipfile.ZipFile(input_zip) as zf:
            files = zf.namelist()
            if not args.verbose:
                files = tqdm(files)
            for f in files:
                s = f.split('_')
                student_name = s[0]

                # Submitted files are named as:
                # <name>[_LATE]_<student id>_<submission id>_<filename>-index

                # skip student name
                s = s[1:]
                # skip LATE
                if s[0] == "LATE":
                    s = s[1:]

                if student_name not in student_ids:
                    student_ids[student_name] = s[0]
                elif student_ids[student_name] != s[0]:
                    # found student with same name but different id!
                    print(f"two students with the same name: {student_name}. ids: {student_ids[student_name]} and {s[0]}")
                    student_name += "_" + s[0]

                # skip student+submission id
                s = s[2:]

                file_name = '_'.join(s)

                # remove '-N' index from multiple submissions
                # find numeric characters at the end of the file preceded by a `-`
                # note: Canvas should give only the most recent submission when downloading all.
                name, ext = os.path.splitext(file_name)
                idx = -1
                while name[idx].isnumeric():
                    idx -= 1
                if name[idx] == '-':
                    name = name[:idx]
                file_name = name + ext

                if args.verbose:
                    print(f"{f}  ->  {student_name}/{file_name}")

                dst = os.path.join(output_folder, student_name)
                if not os.path.exists(dst):
                    os.mkdir(dst)
                    
                try:
                    if f.endswith(".zip"):
                        # Unzip and extract to the folder.
                        with zipfile.ZipFile(zf.open(f)) as zf2:
                            zf2.extractall(dst)
                    else:
                        # Extract the file to the folder.
                        zf.extract(f, dst)
                    
                        os.rename(
                            os.path.join(dst, f),
                            os.path.join(dst, file_name))
                        
                except KeyboardInterrupt:
                    exit()
                except Exception as e:
                    print(f"Exception while extracting {f}: {str(e)}\n")
    except Exception as e:
        print(f"Exception while opening {input_zip}: {str(e)}\n")
    