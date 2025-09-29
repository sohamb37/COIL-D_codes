import os
import pandas as pd

# --- Configuration ---
# The name of your original directory.
SOURCE_DIR = '/home/soham37/python/Domain_Wise_Arranged_Parallel'
# The name of the directory with the filtered data.
FILTERED_DIR = '/home/soham37/python/Filtered_Copy_Domain_Wise_Arranged'
# The specific folders you want to analyze.
FOLDERS_TO_ANALYZE = {'source_translated', 'source_reviewed'}
# The name of the output CSV file for the report.
OUTPUT_CSV = '/home/soham37/python/Stats/line_comparison_old_new_post_filtering.csv'


def count_lines_in_file(filepath):
    """
    Counts the number of lines in a text file.
    Returns 0 if the file is not found or cannot be read.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0
    except Exception as e:
        print(f"Warning: Could not read file {filepath}: {e}")
        return 0

def generate_comparison_report():
    """
    Compares line counts between original and filtered directories,
    and returns the results as a pandas DataFrame.
    """
    comparison_data = []

    print("Starting analysis of directories...")
    for root, dirs, files in os.walk(SOURCE_DIR):
        current_dir_name = os.path.basename(root)

        if current_dir_name in FOLDERS_TO_ANALYZE:
            for filename in files:
                if not filename.endswith('.txt'):
                    continue

                try:
                    original_file_path = os.path.join(root, filename)
                    relative_path_to_file = os.path.relpath(original_file_path, SOURCE_DIR)
                    filtered_file_path = os.path.join(FILTERED_DIR, relative_path_to_file)

                    old_count = count_lines_in_file(original_file_path)
                    filtered_count = count_lines_in_file(filtered_file_path)
                    difference = old_count - filtered_count

                    # --- FIXED METADATA EXTRACTION ---
                    # Get the path of the directory containing the file, relative to the start.
                    # e.g., "AGRI/HIN-ASM/AGRI_SUBDOMAIN/translation_text/source_translated"
                    relative_dir_path = os.path.dirname(relative_path_to_file)
                    path_parts = relative_dir_path.split(os.sep)
                    
                    # Now path_parts[0] will be 'AGRI', path_parts[1] will be 'HIN-ASM', etc.
                    primary_domain = path_parts[0]
                    lang_pair = path_parts[1]
                    sub_domain = path_parts[2]
                    bi_text_type = path_parts[4] # or simply current_dir_name

                    comparison_data.append({
                        'Primary Domain': primary_domain,
                        'Language Pair': lang_pair,
                        'Sub Domain': sub_domain,
                        'Bi-text Type': bi_text_type,
                        'File Name': filename,
                        'Line Count_Old': old_count,
                        'Line Count_Filtered': filtered_count,
                        'Difference': difference
                    })
                    print(f"  - Analyzed: {relative_path_to_file}")

                except IndexError:
                    print(f"Warning: Could not parse metadata from path: '{relative_dir_path}'. Skipping file.")
                except Exception as e:
                    print(f"An unexpected error occurred while processing {original_file_path}: {e}")

    report_df = pd.DataFrame(comparison_data)
    return report_df

# --- Main execution block ---
if __name__ == "__main__":
    if not os.path.isdir(SOURCE_DIR) or not os.path.isdir(FILTERED_DIR):
        print(f"❌ Error: Please ensure both '{SOURCE_DIR}' and '{FILTERED_DIR}' directories exist.")
    else:
        # Create the directory for the output CSV if it doesn't exist
        output_dir = os.path.dirname(OUTPUT_CSV)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        results_df = generate_comparison_report()
        
        if not results_df.empty:
            results_df = results_df.sort_values(by='Difference', ascending=False)
            results_df.to_csv(OUTPUT_CSV, index=False)
            
            print(f"\n✅ Analysis complete! Report saved to '{OUTPUT_CSV}'.")
            print("\nPreview of the report (top 5 files with largest sentence loss):")
            print(results_df.head())
        else:
            print("\nNo files were found to analyze in the specified directories.")