import os
import pandas as pd

# --- Configuration ---
# The specific folders you want to analyze within the target directory.
FOLDERS_TO_ANALYZE = {'source_translated', 'source_reviewed'}

def analyze_file_word_counts(filepath):
    """
    Analyzes a single file to count sentences in predefined word-count bins.

    Args:
        filepath (str): The full path to the text file.

    Returns:
        tuple: A tuple containing the total line count (int) and a dictionary
               with counts for each word-count bin.
    """
    # Initialize bins for word counts
    word_bins = {
        '0-5 words': 0,
        '6-10 words': 0,
        '11-20 words': 0,
        '21-30 words': 0,
        '31-55 words': 0,
        '> 55 words': 0
    }
    total_lines = 0

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                # --- FIX ---
                # 1. Count every line immediately to match the previous script's behavior.
                total_lines += 1

                # 2. Strip the line to check for content.
                stripped_line = line.strip()
                if not stripped_line:
                    # 3. Skip word count analysis for empty lines, but they are now included in total_lines.
                    continue

                # Split by tab to get the source sentence (first column)
                parts = stripped_line.split('\t')
                source_sentence = parts[0]
                
                # Count words by splitting on whitespace
                word_count = len(source_sentence.split())

                # Assign the word count to the correct bin
                if word_count <= 5:
                    word_bins['0-5 words'] += 1
                elif word_count <= 10:
                    word_bins['6-10 words'] += 1
                elif word_count <= 20:
                    word_bins['11-20 words'] += 1
                elif word_count <= 30:
                    word_bins['21-30 words'] += 1
                elif word_count <= 55:
                    word_bins['31-55 words'] += 1
                else: # word_count > 55
                    word_bins['> 55 words'] += 1
                    
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
    except Exception as e:
        print(f"An error occurred while processing {filepath}: {e}")

    return total_lines, word_bins

def generate_distribution_report(target_dir):
    """
    Generates a full report on sentence length distribution for a target directory.

    Args:
        target_dir (str): The path to the directory to analyze.

    Returns:
        pandas.DataFrame: A DataFrame containing the full analysis.
    """
    analysis_data = []
    
    print(f"\nStarting analysis of directory: '{target_dir}'...")
    
    # Walk through the entire target directory tree
    for root, dirs, files in os.walk(target_dir):
        current_dir_name = os.path.basename(root)

        # Only process files inside the specified analysis folders
        if current_dir_name in FOLDERS_TO_ANALYZE:
            for filename in files:
                if not filename.endswith('.txt'):
                    continue

                try:
                    full_path = os.path.join(root, filename)
                    
                    # 1. Analyze the file to get word counts
                    total_lines, word_bins = analyze_file_word_counts(full_path)
                    
                    if total_lines == 0:
                        continue # Skip empty or unreadable files

                    # 2. Extract metadata from the path
                    relative_dir_path = os.path.dirname(os.path.relpath(full_path, target_dir))
                    path_parts = relative_dir_path.split(os.sep)

                    primary_domain = path_parts[0]
                    lang_pair = path_parts[1]
                    sub_domain = path_parts[2]
                    bi_text_type = path_parts[4] # Or simply current_dir_name

                    # 3. Combine all data into a single record
                    record = {
                        'Primary Domain': primary_domain,
                        'Language Pair': lang_pair,
                        'Sub Domain': sub_domain,
                        'Bi-text Type': bi_text_type,
                        'File Name': filename,
                        'Total Lines': total_lines,
                    }
                    # Add the word count bin data to the record
                    record.update(word_bins)
                    
                    analysis_data.append(record)
                    print(f"  - Analyzed: {os.path.relpath(full_path, target_dir)}")

                except IndexError:
                    print(f"Warning: Could not parse metadata from path: '{relative_dir_path}'. Skipping file.")
                except Exception as e:
                    print(f"An unexpected error occurred for file '{filename}': {e}")

    return pd.DataFrame(analysis_data)

# --- Main execution block ---
if __name__ == "__main__":
    # Get the directory path from the user
    input_path = input("Enter the full path to the directory to analyze (e.g., Parent): ").strip()

    if not os.path.isdir(input_path):
        print(f"❌ Error: The directory '{input_path}' does not exist. Please check the path and try again.")
    else:
        results_df = generate_distribution_report(input_path)

        if not results_df.empty:
            # Define the final column order for the CSV file
            column_order = [
                'Primary Domain', 'Language Pair', 'Sub Domain', 'Bi-text Type', 'File Name', 
                'Total Lines', '0-5 words', '6-10 words', '11-20 words', '21-30 words', 
                '31-55 words', '> 55 words'
            ]
            results_df = results_df[column_order]

            # Create a dynamic output filename based on the input folder's name
            base_folder_name = os.path.basename(os.path.normpath(input_path))
            # output_csv_name = f"{base_folder_name}_sentence_distribution.csv"
            output_csv_name = "/home/soham37/python/Stats/word_count_distribution_old.csv"

            # Save the report to a CSV file
            results_df.to_csv(output_csv_name, index=False)
            
            print(f"\n✅ Analysis complete! Report saved to '{output_csv_name}'.")
            print("\nPreview of the report:")
            print(results_df.head())
        else:
            print("\nNo valid files were found to analyze in the specified directory.")

