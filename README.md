# Translation File Processor

A Python script to combine, analyze, and process translation files organized by language pairs and domains. This tool is designed to work with translation project structures containing `source_translated` and `source_reviewed` directories.





## Usage

```bash
# Display statistics only
python3 combine_translated_files.py /path/to/parent/folder

# Full feature usage with all outputs
python3 combine_translated_files.py /path/to/root -c stats.csv

```

## Command Line Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `folder` | - | **Required.** Path to the parent folder containing the translation structure |
| `--output` | `-o` | Directory to save combined text files (organized by language pair/domain) |
| `--json` | `-j` | Path to save statistics as JSON file |
| `--csv` | `-c` | Path to save statistics as CSV file |
| `--consortium` | `-cons` | Path to save combined source_translated files for consortium sharing |

## Expected Folder Structure

The script expects a folder structure like:

```
parent_folder/
├── LANG_PAIR_1/
│   ├── DOMAIN_1/
│   │   ├── source_translated/
│   │   │   ├── file1.txt
│   │   │   └── file2.txt
│   │   └── source_reviewed/
│   │       ├── file1.txt
│   │       └── file2.txt
│   └── DOMAIN_2/
│       └── source_translated/
│           └── file3.txt
└── LANG_PAIR_2/
    └── DOMAIN_1/
        └── source_translated/
            └── file4.txt
```

### Supported Elements

- **Language Pairs**: HIN-MAI, HIN-SIN, HIN-BAN, etc.
- **Domains**: EDU, HLT, AGRI, GOV, JUD, TOUR
- **File Types**: `source_translated`, `source_reviewed`

## Output

### CSV Output
When using the `-c` option, generates a CSV file with tabular data suitable for spreadsheet applications containing:
- Language Pair
- Domain  
- Type
- Files
- Lines
- Words

## File Processing Details

### Header Handling
The script intelligently handles duplicate headers in text files:
- Recognizes headers: `Source_Text`, `Translated_Text`, `Reviewed_Text`
- Ensures each header type appears only once in combined output
- Preserves all content while avoiding duplication

### Word and Line Counting
- **Lines**: Counts non-empty lines, excluding header lines
- **Words**: Counts words in the first tab-separated column of each line
- Provides accurate statistics for translation work assessment

### Cleanup Operations
- Automatically removes `translation_domain_terms` folders
- Maintains clean directory structure
- Preserves only essential translation directories

## Examples

### Example 1: Basic Statistics
```bash
python3 combine_translated_files.py /projects/translation_data
```
Output: Console statistics table

### Example 2: Generate CSV Statistics
```bash
python3 combine_translated_files.py /projects/translation_data -c statistics.csv
```
Output: Console statistics and CSV file

## Notes

- The script uses UTF-8 encoding for all file operations
- Empty lines and header-only files are handled gracefully
- Statistics exclude header lines for accurate content measurement


# Folder Matching and Moving Script

A Python utility for matching and moving folders between different directory structures, with preprocessing capabilities for zip files and folder cleanup.

## Overview

This script is designed to move folders from the newly downloaded folder to the old_parent directory:
- **Old Parent Structure**: `old_parent/languages/domains/actual_folders`
- **New Folder Structure**: `new_folder/actual_folders`

The script matches folders by name and moves them from the new folder structure to replace corresponding folders in the old parent structure.

## Features

- **Folder Matching**: Automatically matches folders by name between different directory structures
- **Preprocessing**: Unzips files, removes unwanted folders, and cleans up empty directories
- **Safe Operations**: Dry-run mode by default to preview changes before execution
- **Interactive Confirmations**: Built-in prompts to prevent accidental operations
- **Comprehensive Logging**: Detailed output showing all operations and results

## Usage

### Basic Syntax

```bash
python script.py <old_parent_path> <new_folder_path> [options]
```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `old_parent_path` | Path to the old parent folder with structure: `old_parent/languages/domains/actual_folders` |
| `new_folder_path` | Path to the new folder with structure: `new_folder/actual_folders` |
| `--preprocess` | Preprocess the new folder (unzip files, remove unwanted folders, clean empty directories) |


### Example Commands

1. **Basic dry-run** (safe preview):
   ```bash
   python script.py /path/to/old_parent /path/to/new_folder
   ```

2. **With preprocessing**:
   ```bash
   python script.py /path/to/old_parent /path/to/new_folder --preprocess
   ```

## Directory Structures

### Old Parent Structure
```
old_parent/
├── language1/
│   ├── domain1/
│   │   ├── folder_a/
│   │   ├── folder_b/
│   │   └── folder_c/
│   └── domain2/
│       ├── folder_d/
│       └── folder_e/
└── language2/
    └── domain3/
        ├── folder_f/
        └── folder_g/
```

### New Folder Structure
```
new_folder/
├── folder_a/
├── folder_b/
├── folder_x/  (no match in old_parent)
└── folder_y/  (no match in old_parent)
```

## Preprocessing Features

When `--preprocess` is used, the script performs the following operations on the new folder:

1. **Unzip Files**: Extracts all `.zip` files and removes the original zip files
2. **Remove Unwanted Folders**: Deletes all folders named "translation_domain_terms"
3. **Clean Empty Folders**: Removes directories that contain no files (multiple passes for nested empty folders)

## Output Example

```
============================================================
FOLDER MATCHING AND MOVING SCRIPT
============================================================
Old parent path: /path/to/old_parent
New folder path: /path/to/new_folder
Dry run mode: True
============================================================

Found in old_parent: folder_a at /path/to/old_parent/lang1/domain1/folder_a
Found in old_parent: folder_b at /path/to/old_parent/lang1/domain1/folder_b
Found in new_folder: folder_a at /path/to/new_folder/folder_a
Found in new_folder: folder_x at /path/to/new_folder/folder_x

Found 2 folders in old_parent
Found 2 folders in new_folder

Found 1 matching folders:
  - folder_a

========================================
Processing: folder_a
From: /path/to/new_folder/folder_a
To:   /path/to/old_parent/lang1/domain1/folder_a
  [DRY RUN] Would remove existing folder and move new one

========================================
SUMMARY:
========================================
Would move 1 folders
Remaining folders in new_folder: 1
  - folder_x
```

## Important Notes

- **Destructive Operation**: The script removes existing folders in the old parent structure before moving new ones
- **Use Dry-run First**: Always review

# Bi-weekly Statistics

Bi-weekly statistics calculated by merging 2 week's csv files and then getting the difference in terms of lines and words. 

# Finally...

Import the csv files in Excel or Google Sheets and conduct your analysis.


