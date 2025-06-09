
# DICOM Tag Editor

This is a Python application to edit DICOM tags in a DICOM series using the `pydicom` library.

## Features
- Load a directory of DICOM files (a series)
- List and edit DICOM tags for all files in the series
- Save changes to the DICOM files

## Requirements
- Python 3.7+
- pydicom

## Installation

1. Install dependencies:
   ```bash
   pip install pydicom
   ```

## Usage

Run the app:

```bash
python dicom_tag_editor.py /path/to/dicom/series --tag PatientName --value "New Name"
```

- `--tag`: The DICOM tag keyword (e.g., PatientName, StudyDate)
- `--value`: The new value to set for the tag

You can also run without `--tag` and `--value` to list tags in the series.

## Example

```bash
python dicom_tag_editor.py ./dicom_series --tag PatientID --value 12345
```

This will set the PatientID tag to 12345 for all DICOM files in the specified directory.

---

This tool is for research and educational use. Always keep backups of your original DICOM data.
