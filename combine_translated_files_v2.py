# How to use:
'''

using v8
python3 combine_translated_files.py /path/to/parent/folder - just get the stats after combining
python3 combine_translated_files.py /path/to/parent/folder -o combined_output.txt - write down the combined files as well
python combine_translated_files.py /path/to/root -o output_directory -j stats.json -c stats.csv

'''

import os
import re
import shutil
import json
import argparse
import pandas as pd
from pathlib import Path
from collections import defaultdict

def find_source_translated_dirs(parent_folder):
    """Find all source_translated directories in the folder structure."""
    source_translated_dirs = []
    
    for root, dirs, files in os.walk(parent_folder):
        if os.path.basename(root) == "source_translated":
            source_translated_dirs.append(root)
    
    return source_translated_dirs

def delete_extra_folders(parent_folder):
    """Delete all folders except source_translated, source_reviewed and translated_reviewed directories in the parent folder"""
    for root, dirs, files in os.walk(parent_folder):
        if os.path.basename(root) == "translation_domain_terms":
            shutil.rmtree(root)

def find_translation_dirs(parent_folder):
    """Find all source_translated and source_reviewed directoris with their language pair and domain info"""
    translation_dirs = []

    for root, dirs, files in os.walk(parent_folder):
        if os.path.basename(root) in ["source_translated", "source_reviewed"]:
            folder_type = os.path.basename(root)

            # Try to identify language pair and domain from the path
            path_parts = Path(root).parts
            lang_pair = None
            domain = None

            # Look for language pairs (HIN-MAI, HIN-SIN, HIN-BAN, etc.)
            for part in path_parts:
                if part.startswith("HIN-") or "-" in part:  # Simple heuristic for language pairs
                    lang_pair = part
                    break
            
            # Look for domains (EDU, HLT, AGRI, etc.)
            for part in path_parts:
                if part in ["EDU", "HLT", "AGRI", "GOV", "JUD", "TOUR"]:
                    domain = part
                    break
            
            translation_dirs.append({
                "path": root,
                "type": folder_type,
                "lang_pair": lang_pair,
                "domain": domain
            })
    
    return translation_dirs


def process_translation_files(directories):
    """Process all txt files from the given directories and organize by language pair and domain."""
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"files": 0, "lines": 0, "words": 0, "combined_text": ""})))
    
    for dir_info in directories:
        path = dir_info["path"]
        folder_type = dir_info["type"]
        lang_pair = dir_info["lang_pair"] or "Unknown"
        domain = dir_info["domain"] or "Unknown"
        
        combined_text = ""
        file_count = 0
        
        for file in os.listdir(path):
            if file.endswith(".txt"):
                file_path = os.path.join(path, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        combined_text += text + "\n"
                    file_count += 1
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
        
        if combined_text:
            line_count, word_count = count_lines_and_words(combined_text)
            
            stats[lang_pair][domain][folder_type]["files"] += file_count
            stats[lang_pair][domain][folder_type]["lines"] += line_count
            stats[lang_pair][domain][folder_type]["words"] += word_count
            stats[lang_pair][domain][folder_type]["combined_text"] += combined_text
    
    return stats

# def combine_txt_files(directories):
#     """Combine all txt files from the given directories."""
#     combined_text = ""
#     file_count = 0
    
#     for directory in directories:
#         for file in os.listdir(directory):
#             if file.endswith(".txt"):
#                 file_path = os.path.join(directory, file)
#                 try:
#                     with open(file_path, 'r', encoding='utf-8') as f:
#                         combined_text += f.read() + "\n"
#                     file_count += 1
#                 except Exception as e:
#                     print(f"Error reading file {file_path}: {e}")
    
#     return combined_text, file_count

def count_lines_and_words(text):
     
    """Count lines and words in the text, excluding lines that contain 'Translated_Text', 'Reviewed_Text', or 'Source_Text'."""
    # Split text by newline characters to get all lines
    lines = text.splitlines()

    # Filter out lines containing the specified words and empty lines
    filtered_lines = []
    for line in lines:
        line_stripped = line.strip()
        if (line_stripped and 
            "Translated_Text" not in line and 
            "Reviewed_Text" not in line and 
            "Source_Text" not in line):
            filtered_lines.append(line)

    line_count = len(filtered_lines)

    word_count = 0
    for line in lines:
        word_count += len(line.split("\t")[0].split())

    return line_count, word_count   


# def count_lines_and_words(text):
#     """Count lines and words in the text."""
#     # Split text by newline characters to count lines
#     lines = text.splitlines()
#     # Remove empty lines
#     lines = [line for line in lines if line.strip()]
#     line_count = len(lines)
    
#     word_count = 0
#     for line in lines:
#         word_count += len(line.split("\t")[0].split())
    
#     return line_count, word_count

def display_stats(stats, csv_file=None):
    """Display statistics in a readable format and save to DataFrame if csv_file is provided."""
    print("\n=== Language Pair and Domain-wise Statistics ===\n")
    
    # Calculate total stats
    total_files = 0
    total_lines = 0
    total_words = 0
    
    # Create a summary table
    print(f"{'Language Pair':<12} | {'Domain':<6} | {'Type':<18} | {'Files':<6} | {'Lines':<8} | {'Words':<10}")
    print("-" * 70)

    # Create a list to store data for DataFrame
    df_data = []
    
    for lang_pair, domains in sorted(stats.items()):
        for domain, types in sorted(domains.items()):
            for folder_type, data in sorted(types.items()):
                files = data["files"]
                lines = data["lines"]
                words = data["words"]
                
                print(f"{lang_pair:<12} | {domain:<6} | {folder_type:<18} | {files:<6} | {lines:<8} | {words:<10}")
                
                # Add data for DataFrame
                df_data.append({
                    "Language Pair": lang_pair,
                    "Domain": domain,
                    "Type": folder_type,
                    "Files": files,
                    "Lines": lines,
                    "Words": words
                })

                total_files += files
                total_lines += lines
                total_words += words
    
    print("-" * 70)
    print(f"{'TOTAL':<12} | {'':<6} | {'':<18} | {total_files:<6} | {total_lines:<8} | {total_words:<10}")

    # Add total row for DataFrame
    df_data.append({
        "Language Pair": "TOTAL",
        "Domain": "",
        "Type": "",
        "Files": total_files,
        "Lines": total_lines,
        "Words": total_words
    })

    # Create DataFrame
    df = pd.DataFrame(df_data)

    # Save to CSV if file path is provided
    if csv_file:
        df.to_csv(csv_file, index=False)
        print(f"\nStatistics saved to CSV file: {csv_file}")
    
    return df

def save_combined_text(stats, output_dir):
    """Save combined text files organized by language pair, domain, and type."""
    for lang_pair, domains in stats.items():
        for domain, types in domains.items():
            for folder_type, data in types.items():
                if data["combined_text"]:
                    # Create directory structure
                    output_path = os.path.join(output_dir, lang_pair, domain)
                    os.makedirs(output_path, exist_ok=True)
                    
                    # Save combined text
                    file_path = os.path.join(output_path, f"{folder_type}.txt")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(data["combined_text"])
                    
                    print(f"Saved combined text to {file_path}")

def save_stats_json(stats, output_file):
    """Save statistics as JSON file."""
    # Convert defaultdict to regular dict for JSON serialization
    json_stats = {}
    
    for lang_pair, domains in stats.items():
        json_stats[lang_pair] = {}
        for domain, types in domains.items():
            json_stats[lang_pair][domain] = {}
            for folder_type, data in types.items():
                # Don't include the combined text in JSON output
                json_stats[lang_pair][domain][folder_type] = {
                    "files": data["files"],
                    "lines": data["lines"],
                    "words": data["words"]
                }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_stats, f, indent=2)
    
    print(f"Saved statistics to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Analyze translation files by language pair and domain")
    parser.add_argument("folder", help="Path to the parent folder containing the folder structure")
    parser.add_argument("-o", "--output", help="Directory to save the combined text files (optional)")
    parser.add_argument("-j", "--json", help="Path to save statistics as JSON (optional)")
    parser.add_argument("-c", "--csv", help="Papython3 combine_translated_files.py /path/to/parent/folder -o combined_output.txtth to save statistics as CSV (optional)")
    
    args = parser.parse_args()
    parent_folder = args.folder
    output_dir = args.output
    json_file = args.json
    csv_file = args.csv
    
    if not os.path.isdir(parent_folder):
        print(f"Error: {parent_folder} is not a valid directory")
        return
    
    print("Deleting the domain_translation_terms extra folders")
    delete_extra_folders(parent_folder)


    print(f"Searching for translation directories in {parent_folder}...")
    translation_dirs = find_translation_dirs(parent_folder)
    
    if not translation_dirs:
        print("No translation directories found.")
        return
    
    print(f"Found {len(translation_dirs)} translation directories.")
    
    # Process files and calculate statistics
    stats = process_translation_files(translation_dirs)
    
    # Display the statistics and collect the df
    df = display_stats(stats, csv_file)
    
    # Save combined text files if output directory is specified
    if output_dir:
        save_combined_text(stats, output_dir)
    
    # Save statistics as JSON if specified
    if json_file:
        save_stats_json(stats, json_file)

    # return df

if __name__ == "__main__":
    main()