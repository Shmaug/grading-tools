import os
import argparse
from pathlib import Path
import platform
import subprocess
import cv2

def vscode_on_file(path):
    try:
        subprocess.run(['code', path], shell=True)
    except Exception as e:
        print(f"Failed to open vscode: {str(e)}")

def explorer_on_file(path):
    path = os.path.abspath(path)
    system = platform.system()
    try:
        if system == "Windows":
            # reveal in Explorer
            subprocess.Popen(['explorer', path])
            return
        if system == "Darwin":
            # reveal in Finder
            subprocess.Popen(['open', '-R', path])
            return
    except Exception as e:
        print(f"Could not open file explorer for {path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Canvas student submission comparison utility.')
    parser.add_argument('submissions_dir', help='Directory containing the images to compare, i.e., the student subfolder.')
    parser.add_argument('--student',       required=False, help='Start at a student subfolder name or index.')
    args = parser.parse_args()

    students = sorted(os.listdir(args.submissions_dir))

    window_name = "image grader"
    cv2.namedWindow(window_name)

    src_img  = None
    student_index = 0
    student_images = []
    img_index = 0

    if args.student is not None:
        if str(args.student).isnumeric():
            student_index = int(args.student)
        elif args.student not in students:
            print(f"No student {args.student} found.")
        else:
            student_index = students.index(args.student)

    def update_window():
        img_name = student_images[img_index] if img_index < len(student_images) else ""
        cv2.setWindowTitle(window_name, f"{students[student_index]}/{img_name} ({student_index+1}/{len(students)})")
        cv2.imshow(window_name, src_img)

    def load_images():
        global src_img
        global student_images
        global img_index

        src_img = None

        student_folder = os.path.join(args.submissions_dir, students[student_index])
    
        # try to find file with matching name
        student_images = []
        for s in Path(student_folder).rglob("*.png"):
            if not os.path.basename(s).startswith("."):
                student_images.append(s)
        if len(student_images) == 0:
            print(f"No images found for student: {students[student_index]}")
            update_window()
            return

        src_img = cv2.imread(student_images[img_index], cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
        if src_img is None:
            print(f"Failed to load {student_images[img_index]}")
            update_window()
            return

        update_window()

    load_images()

    while True:
        try:
            key = cv2.waitKey(50)
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            if key == -1:
                continue
            elif key == 27 or key == ord('q'): # 27=esc
                break
            elif key == ord('n'): # previous student
                student_index = max(student_index-1, 0)
                img_index = 0
                load_images()
            elif key == ord('m'): # next student
                student_index = min(student_index+1, len(students)-1)
                img_index = 0
                load_images()
            elif key == ord(','): # previous image
                img_index -= 1
                if img_index < 0:
                    if student_index > 0:
                        student_index -= 1
                        img_index = 0
                    else:
                        img_index = 0
                load_images()
            elif key == ord('.'): # next image
                img_index += 1
                if img_index >= len(student_images):
                    if student_index < len(students)-1:
                        student_index += 1
                        img_index = 0
                    else:
                        img_index = len(student_images)-1
                load_images()
            elif key == ord('o'): # view submitted files in file browser
                done = False
                for f in Path(os.path.join(args.submissions_dir, students[student_index])).rglob("*.png"):
                    print(os.path.dirname(f))
                    done = True
                    explorer_on_file(os.path.dirname(f))
                    break
                if not done:
                    explorer_on_file(os.path.join(args.submissions_dir, students[student_index]))
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            exit()
            
    cv2.destroyAllWindows()