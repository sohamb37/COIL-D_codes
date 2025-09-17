import os
import csv
import argparse
import sys
from collections import defaultdict

def find_translations(source_file_path, data_directory, output_file_path):
    """
    Finds and aggregates translations for a list of source sentences from a
    structured directory of translation files.

    Args:
        source_file_path (str): Path to a text file with one source sentence per line.
        data_directory (str): Path to the root directory containing the language pair folders.
        output_file_path (str): Path for the output TSV file.
    """
    # --- 1. Read the source sentences to search for ---
    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            # Use a set for efficient O(1) average time complexity lookups
            source_sentences_to_find = {line.strip() for line in f if line.strip()}
        print(f"Loaded {len(source_sentences_to_find)} unique source sentences to find.")
    except FileNotFoundError:
        print(f"Error: The source sentence file was not found at '{source_file_path}'", file=sys.stderr)
        sys.exit(1)

    # --- 2. Scan the directory and build a map of translations ---
    # This will store our results in the format:
    # { "source_sentence": {"LANG_PAIR_1": "translation_1", "LANG_PAIR_2": "translation_2"} }
    found_translations = {sentence: {} for sentence in source_sentences_to_find}
    all_lang_pairs = set()

    print(f"Scanning data directory: '{data_directory}'...")
    
    # os.walk is perfect for traversing the entire directory tree
    for dirpath, dirnames, filenames in os.walk(data_directory):
        # We only care about folders specifically named 'source_reviewed'
        if os.path.basename(dirpath) == 'source_reviewed':
            
            # Extract the language pair from the directory path.
            # It's the first directory inside the main data_directory.
            try:
                # relpath gives us the path relative to the data_directory root
                # e.g., "HIN-BAN/AGRI/EDU_NCERT_PHY/translation_text/source_reviewed"
                relative_path = os.path.relpath(dirpath, data_directory)
                # The first part of this path is the language pair
                lang_pair = relative_path.split(os.sep)[0]
                all_lang_pairs.add(lang_pair)
            except (IndexError, ValueError):
                # Skip if the path structure is not as expected
                continue

            # Now process all text files within this 'source_reviewed' folder
            for filename in filenames:
                if filename.endswith('.txt'):
                    file_path = os.path.join(dirpath, filename)
                    try:
                        with open(file_path, 'r', newline='', encoding='utf-8') as infile:
                            reader = csv.reader(infile, delimiter='\t')
                            for row in reader:
                                # Ensure the row is valid (has at least source and translation)
                                if len(row) >= 2:
                                    source_text = row[0]
                                    translation_text = row[1]
                                    
                                    # If this is one of the sentences we are looking for...
                                    if source_text in source_sentences_to_find:
                                        # ...store the translation under its language pair.
                                        found_translations[source_text][lang_pair] = translation_text
                    except Exception as e:
                        print(f"Warning: Could not process file {file_path}. Error: {e}", file=sys.stderr)

    print("Directory scan complete. Aggregating results...")

    # --- 3. Write the aggregated results to the output TSV file ---
    sorted_lang_pairs = sorted(list(all_lang_pairs))
    
    try:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            
            # Create and write the header row
            header = ['source'] + sorted_lang_pairs
            writer.writerow(header)
            
            # Write the data for each source sentence
            for sentence in sorted(list(source_sentences_to_find)):
                row_data = [sentence]
                translations = found_translations[sentence]
                
                # For each language pair in our header, get the translation.
                # Use .get() to return an empty string if no translation was found.
                for lang_pair in sorted_lang_pairs:
                    row_data.append(translations.get(lang_pair, '')) # Appends empty string if not found
                    
                writer.writerow(row_data)

        print(f"\nSuccessfully created the translation report at '{output_file_path}'.")
        print(f"Found translations for {len(all_lang_pairs)} language pairs: {', '.join(sorted_lang_pairs)}")

    except Exception as e:
        print(f"\nAn unexpected error occurred while writing the output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search for source sentences in a structured directory and return a TSV of all available translations."
    )
    
    parser.add_argument(
        "source_file",
        help="Path to the text file containing source sentences to search for (one per line)."
    )
    
    parser.add_argument(
        "data_directory",
        help="Path to the root data directory that contains the language-pair folders (e.g., HIN-BAN, HIN-ODI)."
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Path for the final merged output TSV file."
    )
    
    args = parser.parse_args()
    
    find_translations(args.source_file, args.data_directory, args.output)
