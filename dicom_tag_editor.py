import os
import argparse
import pydicom
from pydicom.errors import InvalidDicomError


def list_dicom_files(directory):
    """Return a list of DICOM file paths in the given directory."""
    dicom_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                ds = pydicom.dcmread(path, stop_before_pixels=True)
                dicom_files.append(path)
            except InvalidDicomError:
                continue
    return dicom_files


def list_tags(ds):
    """Print all tags and values in the DICOM dataset."""
    for elem in ds:
        print(f"{elem.keyword or elem.tag}: {elem.value}")


def edit_tag_in_series(directory, tag, value):
    files = list_dicom_files(directory)
    for file in files:
        ds = pydicom.dcmread(file)
        if hasattr(ds, tag):
            setattr(ds, tag, value)
            ds.save_as(file)
            print(f"Updated {tag} in {file}")
        else:
            # Try to add the tag if it doesn't exist (e.g., SeriesDescription)
            try:
                ds.add_new(pydicom.datadict.tag_for_keyword(tag), pydicom.datadict.dictionary_VR(tag), value)
                ds.save_as(file)
                print(f"Added {tag} to {file}")
            except Exception as e:
                print(f"Could not add {tag} to {file}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Edit DICOM tags in a series.")
    parser.add_argument("directory", help="Path to DICOM series directory")
    parser.add_argument("--tag", help="DICOM tag keyword to edit (e.g., PatientName)")
    parser.add_argument("--value", help="New value for the tag")
    args = parser.parse_args()

    files = list_dicom_files(args.directory)
    if not files:
        print("No DICOM files found.")
        return

    if args.tag and args.value is not None:
        edit_tag_in_series(args.directory, args.tag, args.value)
    else:
        print(f"Listing tags for first DICOM file: {files[0]}")
        ds = pydicom.dcmread(files[0])
        list_tags(ds)


if __name__ == "__main__":
    main()
