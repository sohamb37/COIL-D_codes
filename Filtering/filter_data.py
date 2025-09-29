import os
import shutil

# --- Configuration ---
# The name of your original parent directory.
SOURCE_PARENT_DIR = '/home/soham37/python/Domain_Wise_Arranged_Parallel'
# The name of the new directory that will be created to store the filtered data.
DEST_PARENT_DIR = '/home/soham37/python/Filtered_Copy_Domain_Wise_Arranged'
# A set of the specific folder names you want to copy and process.
FOLDERS_TO_PROCESS = {'source_translated', 'source_reviewed'}
# The word count limits for the source sentences.
MIN_WORDS = 6
MAX_WORDS = 55

def filter_and_copy_file(source_path, dest_path):
    """
    Reads a source file, filters its lines based on word count in the first column,
    and writes the valid lines to the destination file.
    Assumes the file is tab-separated.
    """
    try:
        # Keep a count of lines before and after filtering.
        lines_before = 0
        lines_after = 0
        
        with open(source_path, 'r', encoding='utf-8') as src_file, \
             open(dest_path, 'w', encoding='utf-8') as dest_file:
            
            for line in src_file:
                lines_before += 1
                # Split the line by tab to separate source and target text.
                parts = line.strip().split('\t')
                
                # Ensure the line has at least a source and a target part.
                if len(parts) >= 2:
                    source_sentence = parts[0]
                    # Count words by splitting the sentence by spaces.
                    word_count = len(source_sentence.split())

                    # Check if the word count is within the desired range.
                    if MIN_WORDS <= word_count <= MAX_WORDS:
                        dest_file.write(line)
                        lines_after += 1
                        
        print(f"    - Filtered '{os.path.basename(source_path)}': Kept {lines_after} of {lines_before} lines.")

    except FileNotFoundError:
        print(f"Warning: Source file not found: {source_path}")
    except Exception as e:
        print(f"An error occurred while processing {source_path}: {e}")

def process_directories(source_dir, dest_dir):
    """
    Walks through the source directory, replicates a filtered structure,
    and processes files based on the rules defined in the configuration.
    """
    print(f"Starting the filtering process from '{source_dir}' to '{dest_dir}'...")

    # Walk through the entire source directory tree.
    for root, dirs, files in os.walk(source_dir, topdown=True):
        
        # --- 1. Prune the directory list to skip unwanted folders ---
        # This modification of 'dirs' in-place tells os.walk() not to descend
        # into the 'translated_reviewed' directory. This is highly efficient.
        if 'translated_reviewed' in dirs:
            dirs.remove('translated_reviewed')

        # --- 2. Create the corresponding directory structure in the destination ---
        relative_path = os.path.relpath(root, source_dir)
        dest_root = os.path.join(dest_dir, relative_path)
        
        # Create the directory if it doesn't exist.
        if not os.path.exists(dest_root):
            os.makedirs(dest_root)

        # --- 3. Check if the current directory is one we need to process ---
        current_dir_name = os.path.basename(root)
        if current_dir_name in FOLDERS_TO_PROCESS:
            print(f"\n[INFO] Processing folder: {root}")
            
            # Process each file in this directory
            for filename in files:
                if filename.endswith('.txt'):
                    source_file_path = os.path.join(root, filename)
                    dest_file_path = os.path.join(dest_root, filename)
                    
                    filter_and_copy_file(source_file_path, dest_file_path)

# --- Main execution block ---
if __name__ == "__main__":
    # Check if the source directory exists before starting.
    if not os.path.isdir(SOURCE_PARENT_DIR):
        print(f"❌ Error: Source directory '{SOURCE_PARENT_DIR}' not found.")
        print("Please ensure this script is in the same location as the 'Parent' folder, or update the SOURCE_PARENT_DIR variable.")
    else:
        # Remove the destination directory if it exists for a fresh start.
        if os.path.exists(DEST_PARENT_DIR):
            print(f"Removing existing destination directory: {DEST_PARENT_DIR}")
            shutil.rmtree(DEST_PARENT_DIR)
        
        process_directories(SOURCE_PARENT_DIR, DEST_PARENT_DIR)
        print("\n✅ Filtering and copying process completed successfully!")
        print(f"The new, filtered directory is available at: '{DEST_PARENT_DIR}'")