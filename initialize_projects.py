import argparse
import colorama
from pathlib import Path
import os
import shutil
import zipfile
import tqdm

# This script provides utilities for processing student submissions. It initializees the homework project by patching submitted files
# into the starter code.
 
# Builds a lookup table which maps file names to the subdirectories they belong in
def build_subdir_luts(starter_code_path, ignore_list=[]):
    lut = {}

    todo = []
    
    for f in os.listdir(starter_code_path):
        todo.append(f)

    while len(todo) > 0:
        filepath = todo.pop()

        ignore = False
        for f in ignore_list:
            if f in filepath or f in filepath.replace('\\', '/'):
                ignore = True
                break
        if ignore:
            continue
        
        fullpath = os.path.join(starter_code_path, filepath)
        if os.path.isdir(fullpath):
            for f in os.listdir(fullpath):
                todo.append(os.path.join(filepath, f))
        else:
            dirname  = os.path.dirname(filepath)
            if os.path.basename(filepath) != '':
                lut[os.path.basename(filepath)] = dirname
            if os.path.basename(dirname) != '':
                lut[os.path.basename(dirname)] = dirname
    
    return lut

# Recursively copies code files to the output directory
def process_submitted_file(output_student_folder, subdir_luts, filepath:str, parent_zipfile:zipfile.ZipFile, file_list=[]):
    if "__MACOSX" in filepath or ".DS_Store" in filepath or ".git" in filepath:
        return
    
    # Recursively process subdirectories
    if parent_zipfile is None and os.path.isdir(filepath):
        for f in os.listdir(filepath):
            process_submitted_file(output_student_folder, subdir_luts, os.path.join(filepath, f), None, file_list)
        return
    
    # Recursively process zipped files
    if filepath.endswith('.zip'):
        f = filepath if parent_zipfile is None else parent_zipfile.open(filepath)
        with zipfile.ZipFile(f) as zf:
            for zipped_file in zf.namelist():
                if not zipped_file.endswith('/'):
                    process_submitted_file(output_student_folder, subdir_luts, zipped_file, zf, file_list)
        if parent_zipfile is not None:
            f.close()
        return
    
    if not any([ f in filepath for f in file_list ]):
        return
    
    # Copy submitted files to the student folder
    dst_dir = os.path.join(output_student_folder, 'submitted_extras')

    src_basename = os.path.basename(filepath)

    should_print = not args.silent

    # Use subdir luts to find the matching subdirectory in the reference code
    if src_basename in subdir_luts:
        # Match filename
        dst_dir = os.path.join(output_student_folder, subdir_luts[src_basename])
        if should_print:
            print(colorama.Fore.GREEN, end='')
    else:
        # Match subdirectory name
        p = os.path.dirname(filepath)
        c = ''
        while p != '':
            if os.path.basename(p) in subdir_luts:
                dst_dir = os.path.join(output_student_folder, subdir_luts[os.path.basename(p)], c)
                if should_print:
                    print(colorama.Fore.CYAN, end='')
                break
            else:
                c = os.path.join(c, os.path.basename(p))
                if p == os.path.dirname(p):
                    break
                p = os.path.dirname(p)
    
    dst_path = os.path.join(dst_dir, src_basename)
    if should_print:
        print(f'{filepath}   ->   {dst_path}' + colorama.Style.RESET_ALL)

    if not os.path.exists(os.path.dirname(dst_path)):
        os.makedirs(os.path.dirname(dst_path))
        
    if parent_zipfile is None:
        # copy file directly
        shutil.copyfile(filepath, dst_path)
    else:
        # extract zipped file
        source = parent_zipfile.open(filepath)
        target = open(dst_path, "wb")
        with source, target:
            shutil.copyfileobj(source, target)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Helper to initialize project directories from submitted files.')
    parser.add_argument('starter',         type=str, help='Path to starter code.')
    parser.add_argument('submissions_dir', type=str, help='Path to submissions folder, containing student subfolders.')
    parser.add_argument('output_dir',      type=str, help='Path to output folder, where student projects will be created.')
    parser.add_argument('files',           nargs="+", type=str, help='Comma-separated list of file names to copy. If the file is not found in a student\'s submission, an error message is printed.')
    parser.add_argument('--students',      nargs="+", type=str, help='Only operate on specified students.')
    parser.add_argument('--silent',        action='store_true')
    args = parser.parse_args()

    file_list         = args.files
    input_path        = args.submissions_dir
    output_path       = args.output_dir
    starter_code_path = args.starter

    subdir_luts = build_subdir_luts(starter_code_path)
    students = []

    namelist = os.listdir(input_path)
    if args.silent:
        namelist = tqdm.tqdm(namelist)
    for submitted_filename in namelist:
        student_name = submitted_filename.split('_')[0]
        if args.students is not None and student_name not in args.students:
            continue
        if student_name not in students:
            students.append(student_name)
            if not args.silent:
                print(f'\n{'='*40}  {student_name}  {'='*40}')

        student_folder = os.path.join(output_path, student_name)

        # skip if already initialized
        if not os.path.exists(student_folder):
            # Copy starter code into student folder
            shutil.copytree(starter_code_path, student_folder)
            
        # Copy submitted files to student's folder
        process_submitted_file(student_folder, subdir_luts, os.path.join(input_path, submitted_filename), None, file_list)

        for student_name in students:
            student_folder = os.path.join(input_path, student_name)
            for required_file in file_list:
                found = False
                for s in Path(student_folder).rglob(required_file):
                    found = True
                    break
                if not found:
                    print(colorama.Fore.RED + f"Error: {student_name} is missing required file '{required_file}'!" + colorama.Style.RESET_ALL)