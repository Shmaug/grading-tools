# Canvas Grading Tools

This is a collection of python scripts which help with grading/viewing assignments downloaded from Canvas.

First, make sure you have the `numpy`, `tqdm`, and `opencv-python` python packages.
Then, download all submissions from Canvas, which should be in one giant zip file.
Use `extract_submissions.py` to setup subfolders for each student's submission.
Finally, run `grade_images.py` to compare each student's images to the reference images.

## `extract_submissions.py`
Usage: `python extract_submissions.py <input_zip> <output_folder>`

This tool extracts files from `<input_zip>` into per-student subfolders within `<output_folder>`.
For submitted zip files, the contents are extracted into the student's subfolder.
For submitted loose files, the tool strips the extra metadata added by Canvas to recover the original filename, and extracts it into the student's subfolder.

## `grade_images.py`
Usage: `python grade_images.py <ref_dir> <submissions_dir> <student_name>`

This tool allows the user to flip between the submitted image and the reference image. 
`<ref_dir>` should contain the reference images. `<submissions_dir>` is the root folder containing all students' subfolders. `<student_name>` is the name of the student's subfolder to examine.
Controls:
- 1/2/3: show reference/submission/error images
- comma/period: show previous/next image