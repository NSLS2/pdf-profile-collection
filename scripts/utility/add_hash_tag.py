import os
import glob


# def add_hash_tag(f_path:str, 
#                  folder_key:list | str = ['XRD', 'tth'], 
#                  search_subfolder:bool =True, 
#                  ):

#     for 



#!/usr/bin/env python3

import os
import re

# ============================================================
# User settings
# ============================================================

ROOT_DIR = r"/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/tiff_base/"

# Only process folders whose names contain this keyword
FOLDER_KEYWORD = "tth"

# Only process text files whose names contain this keyword
FILE_KEYWORD = "XRD"

# File extension
FILE_EXTENSION = ".xy"

# ============================================================
# Function to identify a two-column numeric data line
# ============================================================

def is_data_line(line):
    """
    Return True if the line contains two numeric columns.
    Examples:
        1.23  4.56
        1.23e-5   4.56e+3
    """
    pattern = r'^\s*[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?\s+[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?\s*$'
    return bool(re.match(pattern, line))


# ============================================================
# Process one file
# ============================================================

def add_hash_to_headers(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data_started = False
    new_lines = []

    for line in lines:

        stripped = line.strip()

        if not data_started:

            # Detect beginning of data block
            if is_data_line(stripped):
                data_started = True
                new_lines.append(line)
                continue

            # Header line
            if stripped and not stripped.startswith("#"):
                new_lines.append("#" + line)
            else:
                new_lines.append(line)

        else:
            # Data section remains unchanged
            new_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Processed: {filepath}")


# ============================================================
# Search folders and files
# ============================================================

def main():

    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):

        folder_name = os.path.basename(dirpath)

        if FOLDER_KEYWORD not in folder_name:
            continue

        for filename in filenames:

            if (
                FILE_KEYWORD in filename
                and filename.lower().endswith(FILE_EXTENSION)
            ):
                filepath = os.path.join(dirpath, filename)
                add_hash_to_headers(filepath)


if __name__ == "__main__":
    main()