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
Usage: `python grade_images.py <ref_dir> <submissions_dir> --student <student>`

This tool allows the user to browse the submitted images and flip between the submitted and reference images. 
`<ref_dir>` should contain the reference images. `<submissions_dir>` is the root folder containing all students' subfolders.
Optionally, `--student <student>` can be passed in to start at a particular student name or index.
Controls:
- 1/2/3: show reference/submission/error images.
- comma/period: previous/next image.
- n/m: previous/next student.
- o: open student's code folder in the file browser.
- c: open student's source file in vscode.