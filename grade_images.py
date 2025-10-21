import os
import argparse
from pathlib import Path
import numpy as np
import cv2

filename_aliases = {
    "hw_1_6_alpha_circles.png": "hw_1_6_alpha_cirlces.png"
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Canvas student submission comparison utility.')
    parser.add_argument('ref_dir',         help='Directory containing the reference images.')
    parser.add_argument('submissions_dir', help='Directory containing the images to compare, i.e., the student subfolder.')
    parser.add_argument('--student', required=False, help='Start at a student subfolder name or index.')
    args = parser.parse_args()

    if not os.path.exists(args.ref_dir):
        print(f"Error: '{args.ref_dir}' does not exist.")
        exit(1)

    students   = os.listdir(args.submissions_dir)
    ref_images = os.listdir(args.ref_dir)
    
    null_image = np.full((480,640,3), (255,0,255), dtype=np.uint8)
    textsize = cv2.getTextSize("No submission found!", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    cv2.putText(null_image, "No submission found!", ((null_image.shape[1] - textsize[0])//2, (null_image.shape[0] + textsize[1])//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)

    window_name = "image grader"
    cv2.namedWindow(window_name)

    ref_img  = None
    src_img  = None
    diff_img = None
    ref_img_index = 0
    student_index = 0
    mode = "source"

    if args.student is not None:
        if str(args.student).isnumeric():
            student_index = int(args.student)
        elif args.student not in students:
            print(f"No student {args.student} found.")
        else:
            student_index = students.index(args.student)

    def update_window():
        cv2.setWindowTitle(window_name, f"{students[student_index]} ({student_index+1}/{len(students)}) {ref_images[ref_img_index]} [{mode}]")
        if mode == "reference":
            cv2.imshow(window_name, ref_img)
        elif mode == "source":
            cv2.imshow(window_name, src_img if src_img is not None else null_image)
        elif mode == "difference":
            cv2.imshow(window_name, diff_img if diff_img is not None else null_image)

    def load_images():
        global ref_img
        global src_img
        global diff_img
        f = ref_images[ref_img_index]

        ref_img  = cv2.imread(os.path.join(args.ref_dir, f), cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
        src_img  = None
        diff_img = None

        student_folder = os.path.join(args.submissions_dir, students[student_index])
    
        # try to find file with matching name
        src_file = os.path.join(student_folder, f)
        for s in Path(student_folder).rglob(f):
            src_file = s
            break
        if not os.path.exists(src_file) and f in filename_aliases:
            for alias in filename_aliases[f]:
                for s in Path(student_folder).rglob(alias):
                    src_file = s
                    break
                if src_file:
                    break

        if not os.path.exists(src_file):            
            print(f"Could not find {f} in {students[student_index]}")
            update_window()
            return

        src_img = cv2.imread(src_file, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
        if ref_img.shape != src_img.shape:
            print(f"Image size mismatch for {src_file} {ref_img.shape} != {src_img.shape}")
            src_img = None
            update_window()
            return

        ref_img_norm = ref_img.astype(np.float32)/255.0
        diff_img = abs(ref_img_norm - src_img.astype(np.float32)/255.0) / (ref_img_norm + 0.01*np.average(ref_img_norm))
        
        error_image_path = os.path.join(student_folder, "__error_images", os.path.splitext(f)[0] + ".error.png")
        if not os.path.exists(error_image_path):
            os.makedirs(os.path.join(student_folder, "__error_images"), exist_ok=True)
            cv2.imwrite(error_image_path, np.clip(diff_img*255.0, 0, 255.0).astype(np.uint8))

        update_window()

    load_images()

    while True:
        try:
            key = cv2.waitKey(50)
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            if key == -1:
                continue
            elif key == 27: # esc key
                break
            elif key == ord('n'):
                student_index = max(student_index-1, 0)
                load_images()
            elif key == ord('m'):
                student_index = min(student_index+1, len(students)-1)
                load_images()
            elif key == ord(','):
                ref_img_index -= 1
                if ref_img_index < 0:
                    if student_index > 0:
                        student_index -= 1
                        ref_img_index += len(ref_images)
                    else:
                        ref_img_index = 0
                load_images()
            elif key == ord('.'):
                ref_img_index += 1
                if ref_img_index >= len(ref_images):
                    if student_index < len(students)-1:
                        ref_img_index = 0
                        student_index += 1
                    else:
                        ref_img_index = len(ref_images)-1
                load_images()
            elif key == ord('o'):

            elif key == ord('1'):
                mode = "source"
                update_window()
            elif key == ord('2'):
                mode = "reference"
                update_window()
            elif key == ord('3'):
                mode = "difference"
                update_window()
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            exit()
            
    cv2.destroyAllWindows()