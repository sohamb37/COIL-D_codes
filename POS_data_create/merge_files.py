import csv
import argparse
import sys
import os

def merge_tsv_files(input_files, output_file):
    """
    Merges multiple tab-separated (TSV) files vertically.

    It keeps the header from the first file and discards the headers
    from all subsequent files.

    Args:
        input_files (list): A list of paths to the input TSV files.
        output_file (str): The path for the merged output TSV file.
    """
    if not input_files:
        print("Error: No input files were provided.", file=sys.stderr)
        return

    try:
        # Open the output file for writing. 
        # newline='' prevents extra blank rows in the output.
        # encoding='utf-8' is best for translation files.
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter='\t')

            # --- Process the first file ---
            first_file = input_files[0]
            print(f"Processing first file (with header): {first_file}")
            with open(first_file, 'r', newline='', encoding='utf-8') as infile:
                reader = csv.reader(infile, delimiter='\t')
                
                # Read the header from the first file and write it to the output
                header = next(reader)
                writer.writerow(header)
                
                # Write the rest of the rows from the first file
                for row in reader:
                    writer.writerow(row)

            # --- Process the remaining files ---
            for file_path in input_files[1:]:
                print(f"Appending file (skipping header): {file_path}")
                with open(file_path, 'r', newline='', encoding='utf-8') as infile:
                    reader = csv.reader(infile, delimiter='\t')
                    
                    # Skip the header of subsequent files
                    # The 'None' argument prevents an error if a file is empty after the header
                    next(reader, None) 
                    
                    # Write the remaining rows to the output
                    for row in reader:
                        writer.writerow(row)
                        
        print(f"\nSuccessfully merged {len(input_files)} files into '{output_file}'.")

    except FileNotFoundError as e:
        print(f"\nError: The file '{e.filename}' was not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def collect_all_files_from_dir_as_list_of_path(dir_path):
    """
    Finds all files located within any 'source_translated' subdirectory.

    This function walks through the directory tree starting from dir_path and
    collects paths to all files that are inside a folder named
    'source_translated' or any of its subdirectories.

    Args:
        dir_path: The absolute or relative path to the directory to search.

    Returns:
        A list of strings, where each string is the full path to a file
        within a 'source_translated' folder.
        Returns an empty list if the directory does not exist or no such
        files are found.
    """
    filtered_file_paths = []
    if not os.path.isdir(dir_path):
        print(f"Error: Directory not found at '{dir_path}'")
        return filtered_file_paths

    # os.walk iteratively visits each directory in the tree
    for root, dirs, files in os.walk(dir_path):
        # Check if 'source_translated' is a component of the current directory path
        if "translated_reviewed" in root.split(os.sep):
            for filename in files:
                # Construct the full path and add it to our list
                full_path = os.path.join(root, filename)
                filtered_file_paths.append(full_path)

    return filtered_file_paths

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge multiple tab-separated (TSV) files, keeping only the header from the first file."
    )
    
    # parser.add_argument(
    #     "input_files", 
    #     nargs='+',  # This allows for one or more input files
    #     help="One or more paths to the input TSV files to be merged."
    # )

    input_files = collect_all_files_from_dir_as_list_of_path("/home/soham37/python/Parallel_v2/HIN-MNI")
    
    parser.add_argument(
        "-o", "--output", 
        required=True, 
        help="Path for the final merged output file."
    )
    
    args = parser.parse_args()
    
    merge_tsv_files(input_files, args.output)

