#!/usr/bin/env python3
import os
import shutil
import zipfile
import argparse
from pathlib import Path

def preprocess_new_folder(new_folder_path):
    """
    Preprocess the new_folder by:
    1. Unzipping all files in the parent folder
    2. Deleting folders named "translation_domain_terms" wherever they exist
    3. Deleting empty folders (folders with no leaf files)
    """
    new_folder = Path(new_folder_path)
    
    # Step 1: Unzip all files
    for zip_file in new_folder.glob("*.zip"):

        extract_dir = zip_file.with_suffix('')  # Removes .zip extension
        extract_dir.mkdir(exist_ok=True)
        # print(zip_file)
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            # extracted_files = zip_ref.namelist()  # List of files extracted
            # print("Extracted files:")
            # for file in extracted_files:
            #     print(f"  - {zip_file.parent / file}")
    
        zip_file.unlink()

    # Step 2: Delete folders named "translation_domain_terms"
    for folder in new_folder.rglob("translation_domain_terms"):
        if folder.is_dir():
            shutil.rmtree(folder)
    
    # Step 3: Delete empty folders
    def has_files(directory):
        for root, dirs, files in os.walk(directory):
            if files:
                return True
        return False
    
    # Multiple passes to handle nested empty folders
    while True:
        removed_any = False
        all_dirs = [d for d in new_folder.rglob("*") if d.is_dir()]
        all_dirs.sort(key=lambda x: len(x.parts), reverse=True)
        
        for dir_path in all_dirs:
            if dir_path.exists() and not has_files(dir_path):
                shutil.rmtree(dir_path)
                removed_any = True
        
        if not removed_any:
            break

def find_actual_folders_in_old_parent(old_parent_path):
    """
    Find all actual folders in the old_parent structure.
    Structure: old_parent -> languages -> domains -> {actual_folders}
    Returns a dictionary mapping folder names to their full paths.
    """
    actual_folders = {}
    old_parent = Path(old_parent_path)
    
    if not old_parent.exists():
        print(f"Error: {old_parent_path} does not exist")
        return actual_folders
    
    # Navigate through languages -> domains -> actual_folders
    for language_dir in old_parent.iterdir():
        if language_dir.is_dir():
            for domain_dir in language_dir.iterdir():
                if domain_dir.is_dir():
                    for actual_folder in domain_dir.iterdir():
                        if actual_folder.is_dir():
                            folder_name = actual_folder.name
                            actual_folders[folder_name] = actual_folder
                            print(f"Found in old_parent: {folder_name} at {actual_folder}")
    
    return actual_folders

def find_actual_folders_in_old_parent(old_parent_path):
    """
    Find all actual folders in the old_parent structure.
    Structure: old_parent -> languages -> domains -> {actual_folders}
    Returns a dictionary mapping folder names to their full paths.
    """
    actual_folders = {}
    old_parent = Path(old_parent_path)
    
    if not old_parent.exists():
        print(f"Error: {old_parent_path} does not exist")
        return actual_folders
    
    # Navigate through languages -> domains -> actual_folders
    for language_dir in old_parent.iterdir():
        if language_dir.is_dir():
            for domain_dir in language_dir.iterdir():
                if domain_dir.is_dir():
                    for actual_folder in domain_dir.iterdir():
                        if actual_folder.is_dir():
                            folder_name = actual_folder.name
                            actual_folders[folder_name] = actual_folder
                            print(f"Found in old_parent: {folder_name} at {actual_folder}")
    
    return actual_folders

def find_actual_folders_in_new_folder(new_folder_path):
    """
    Find all actual folders in the new_folder.
    Structure: new_folder -> {actual_folders}
    Returns a dictionary mapping folder names to their full paths.
    """
    actual_folders = {}
    new_folder = Path(new_folder_path)
    
    if not new_folder.exists():
        print(f"Error: {new_folder_path} does not exist")
        return actual_folders
    
    for actual_folder in new_folder.iterdir():
        if actual_folder.is_dir():
            folder_name = actual_folder.name
            actual_folders[folder_name] = actual_folder
            print(f"Found in new_folder: {folder_name} at {actual_folder}")
    
    return actual_folders

def move_matching_folders(old_parent_path, new_folder_path, dry_run=True):
    """
    Match folders by name and move from new_folder to old_parent structure.
    
    Args:
        old_parent_path: Path to the old_parent folder
        new_folder_path: Path to the new_folder
        dry_run: If True, only print what would be done without actually moving
    """
    print(f"{'='*60}")
    print(f"FOLDER MATCHING AND MOVING SCRIPT")
    print(f"{'='*60}")
    print(f"Old parent path: {old_parent_path}")
    print(f"New folder path: {new_folder_path}")
    print(f"Dry run mode: {dry_run}")
    print(f"{'='*60}")
    
    # Find folders in both locations
    old_folders = find_actual_folders_in_old_parent(old_parent_path)
    new_folders = find_actual_folders_in_new_folder(new_folder_path)
    
    if not old_folders:
        print("No folders found in old_parent structure")
        return
    
    if not new_folders:
        print("No folders found in new_folder")
        return
    
    print(f"\nFound {len(old_folders)} folders in old_parent")
    print(f"Found {len(new_folders)} folders in new_folder")
    
    # Find matches
    matches = []
    for folder_name in new_folders:
        if folder_name in old_folders:
            matches.append(folder_name)
    
    print(f"\nFound {len(matches)} matching folders:")
    for match in matches:
        print(f"  - {match}")
    
    # Process matches
    moved_count = 0
    for folder_name in matches:
        old_path = old_folders[folder_name]
        new_path = new_folders[folder_name]
        
        print(f"\n{'='*40}")
        print(f"Processing: {folder_name}")
        print(f"From: {new_path}")
        print(f"To:   {old_path}")
        
        if dry_run:
            print("  [DRY RUN] Would remove existing folder and move new one")
        else:
            try:
                # Remove the existing folder in old_parent
                if old_path.exists():
                    shutil.rmtree(old_path)
                    print(f"  Removed existing: {old_path}")
                
                # Move the folder from new_folder to old_parent location
                shutil.move(str(new_path), str(old_path))
                print(f"  Moved: {new_path} -> {old_path}")
                moved_count += 1
                
            except Exception as e:
                print(f"  ERROR: Failed to move {folder_name}: {e}")
    
    # Show remaining folders in new_folder
    remaining_folders = [name for name in new_folders if name not in matches]
    print(f"\n{'='*40}")
    print(f"SUMMARY:")
    print(f"{'='*40}")
    if dry_run:
        print(f"Would move {len(matches)} folders")
    else:
        print(f"Successfully moved {moved_count} folders")
    
    print(f"Remaining folders in new_folder: {len(remaining_folders)}")
    for folder_name in remaining_folders:
        print(f"  - {folder_name}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Match and move folders between directory structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script.py /path/to/old_parent /path/to/new_folder
  python script.py /path/to/old_parent /path/to/new_folder --preprocess
  python script.py /path/to/old_parent /path/to/new_folder --no-dry-run
  python script.py /path/to/old_parent /path/to/new_folder --preprocess --no-dry-run

Directory Structure:
  old_parent: old_parent -> languages -> domains -> {actual_folders}
  new_folder: new_folder -> {actual_folders}
        """
    )
    
    parser.add_argument(
        'old_parent_path',
        help='Path to the old_parent folder (structure: old_parent/languages/domains/actual_folders)'
    )
    
    parser.add_argument(
        'new_folder_path',
        help='Path to the new_folder (structure: new_folder/actual_folders)'
    )
    
    parser.add_argument(
        '--preprocess',
        action='store_true',
        help='Preprocess the new_folder (unzip files, remove translation_domain_terms, clean empty folders)'
    )
    
    parser.add_argument(
        '--no-dry-run',
        action='store_true',
        help='Skip dry-run and proceed directly to actual operations (use with caution)'
    )
    
    parser.add_argument(
        '--skip-confirmation',
        action='store_true',
        help='Skip confirmation prompts (use with caution)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    old_parent = args.old_parent_path.strip()
    new_folder = args.new_folder_path.strip()
    
    # Validate paths
    if not Path(old_parent).exists():
        print(f"Error: old_parent path does not exist: {old_parent}")
        return 1
    
    if not Path(new_folder).exists():
        print(f"Error: new_folder path does not exist: {new_folder}")
        return 1
    
    print(f"{'='*60}")
    print(f"FOLDER MATCHING AND MOVING SCRIPT")
    print(f"{'='*60}")
    print(f"Old parent path: {old_parent}")
    print(f"New folder path: {new_folder}")
    print(f"Preprocess mode: {args.preprocess}")
    print(f"Skip dry-run: {args.no_dry_run}")
    print(f"{'='*60}")
    
    # Preprocess new_folder if requested
    if args.preprocess:
        preprocess_new_folder(new_folder)
        
        if not args.skip_confirmation:
            proceed = input("\nPreprocessing completed. Press Enter to continue or 'q' to quit: ").strip().lower()
            if proceed == 'q':
                print("Operation cancelled.")
                return 0
    
    # Run dry-run first (unless explicitly skipped)
    if not args.no_dry_run:
        print("\n" + "="*60)
        print("RUNNING IN DRY-RUN MODE FIRST (no actual changes)")
        print("="*60)
        move_matching_folders(old_parent, new_folder, dry_run=True)
        
        # Ask for confirmation to proceed (unless skipped)
        if not args.skip_confirmation:
            print(f"\n{'='*60}")
            proceed = input("Do you want to proceed with the actual move? (yes/no): ").strip().lower()
            
            if proceed not in ['yes', 'y']:
                print("Operation cancelled.")
                return 0
    
    # Run actual move operation
    print(f"\n{'='*60}")
    print("RUNNING ACTUAL MOVE OPERATION")
    print("="*60)
    move_matching_folders(old_parent, new_folder, dry_run=False)
    print("\nOperation completed successfully!")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
