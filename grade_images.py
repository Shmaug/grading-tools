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
    parser.add_argument('student_name',    help='Student subfolder name.')
    args = parser.parse_args()

    ref_dir = args.ref_dir

    if not os.path.exists(ref_dir):
        print(f"Error: '{ref_dir}' does not exist.")
        exit(1)

    ref_images = os.listdir(ref_dir)

    student_folder = os.path.join(args.submissions_dir, args.student_name)
    os.makedirs(os.path.join(student_folder, "__error_images"), exist_ok=True)
    
    window_name = args.student_name
    cv2.namedWindow(window_name)

    ref_img = None
    src_img = None
    error_img = None
    ref_img_index = 0
    mode = 0

    def update_window():
        cv2.setWindowTitle(window_name, f"{args.student_name} {ref_images[ref_img_index]} {"[reference]" if mode == 0 else "[src]" if mode == 1 else "[error]"}")
        if mode == 0 and ref_img is not None:
            cv2.imshow(window_name, ref_img)
        elif mode == 1 and src_img is not None:
            cv2.imshow(window_name, src_img)
        elif mode == 2 and error_img is not None:
            cv2.imshow(window_name, error_img)

    def load_images():
        global ref_img
        global src_img
        global error_img
        f = ref_images[ref_img_index]
        ref_file = os.path.join(ref_dir, f)

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
            print(f"Could not find {src_file} in {args.submissions_dir}/{args.student_name}")
            return

        ref_img = cv2.imread(ref_file, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
        src_img = cv2.imread(src_file, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
        if ref_img.shape != src_img.shape:
            print(f"Image size mismatch for {src_file} {ref_img.shape} != {src_img.shape}")
            return

        ref_img_norm = ref_img.astype(np.float32)/255.0
        error_img = abs(ref_img_norm - src_img.astype(np.float32)/255.0) / (ref_img_norm + 0.01*np.average(ref_img_norm))
        
        error_image_path = os.path.join(student_folder, "__error_images", os.path.splitext(f)[0] + ".error.png")
        if not os.path.exists(error_image_path):
            cv2.imwrite(error_image_path, np.clip(error_img*255.0, 0, 255.0).astype(np.uint8))

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
            elif key == ord(','):
                ref_img_index -= 1
                if ref_img_index < 0:
                    ref_img_index += len(ref_images)
                load_images()
            elif key == ord('.'):
                ref_img_index = (ref_img_index + 1) % len(ref_images)
                load_images()
            elif key == ord('1'):
                mode = 0
                update_window()
            elif key == ord('2'):
                mode = 1
                update_window()
            elif key == ord('3'):
                mode = 2
                update_window()
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            exit()
            
    cv2.destroyAllWindows()