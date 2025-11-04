#!/usr/bin/env python3
"""
Python script to run a Photoshop JSX script with file paths from command line
Usage: python run_photoshop_action.py --files "C:\\path\\image1.jpg" "C:\\path\\image2.png" [options]
"""

import subprocess
import sys
import os
import platform
import argparse
import tempfile
import glob

def find_photoshop_path():
    """Find Photoshop executable path based on operating system"""
    system = platform.system()
    
    if system == "Windows":
        # Common Photoshop paths on Windows
        possible_paths = [
            r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe",
            r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
            r"C:\Program Files\Adobe\Adobe Photoshop 2022\Photoshop.exe",
            r"C:\Program Files\Adobe\Adobe Photoshop CC 2019\Photoshop.exe",
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            "/Applications/Adobe Photoshop 2024/Adobe Photoshop 2024.app/Contents/MacOS/Adobe Photoshop 2024",
            "/Applications/Adobe Photoshop 2023/Adobe Photoshop 2023.app/Contents/MacOS/Adobe Photoshop 2023",
            "/Applications/Adobe Photoshop 2022/Adobe Photoshop 2022.app/Contents/MacOS/Adobe Photoshop 2022",
            "/Applications/Adobe Photoshop CC 2019/Adobe Photoshop CC 2019.app/Contents/MacOS/Adobe Photoshop CC 2019",
        ]
    else:
        print(f"Unsupported operating system: {system}")
        return None
    
    # Check which path exists
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def expand_file_patterns(file_patterns):
    """Expand file patterns including wildcards and validate files"""
    expanded_files = []
    
    for pattern in file_patterns:
        # Check if pattern contains wildcards
        if '*' in pattern or '?' in pattern:
            # Expand wildcard pattern
            matched_files = glob.glob(pattern)
            if matched_files:
                expanded_files.extend(matched_files)
            else:
                print(f"Warning: No files matched pattern: {pattern}")
        else:
            # Direct file path
            if os.path.exists(pattern) and os.path.isfile(pattern):
                expanded_files.append(pattern)
            else:
                print(f"Warning: File does not exist: {pattern}")
    
    return expanded_files

def create_jsx_with_files(template_jsx_path, files, action_set=None, action_name=None, suffix=None):
    """Create a temporary JSX file with specified file paths"""
    
    # Read the template JSX file
    with open(template_jsx_path, 'r', encoding='utf-8') as f:
        jsx_content = f.read()
    
    if not files:
        print("Error: No valid files provided!")
        return None
    
    # Convert file paths to proper format with escaped backslashes for Windows
    formatted_files = []
    for file_path in files:
        abs_path = os.path.abspath(file_path)
        if platform.system() == "Windows":
            # Escape backslashes for JavaScript string
            abs_path = abs_path.replace('\\', '\\\\')
        formatted_files.append(abs_path)
    
    # Create files array string
    files_array = '["' + '", "'.join(formatted_files) + '"]'
    
    # Replace the inputFiles array in the JSX content
    import re
    jsx_content = re.sub(
        r'var inputFiles = \[.*?\];',
        f'var inputFiles = {files_array};',
        jsx_content,
        flags=re.DOTALL
    )
    
    # Optionally replace action set name
    if action_set:
        jsx_content = re.sub(
            r'var actionSetName = ".*?";',
            f'var actionSetName = "{action_set}";',
            jsx_content
        )
    
    # Optionally replace action name
    if action_name:
        jsx_content = re.sub(
            r'var actionName = ".*?";',
            f'var actionName = "{action_name}";',
            jsx_content
        )
    
    # Optionally replace suffix
    if suffix:
        jsx_content = re.sub(
            r'var suffix = ".*?";',
            f'var suffix = "{suffix}";',
            jsx_content
        )
    
    # Create temporary JSX file
    temp_jsx = tempfile.NamedTemporaryFile(mode='w', suffix='.jsx', delete=False, encoding='utf-8')
    temp_jsx.write(jsx_content)
    temp_jsx.close()
    
    return temp_jsx.name

def get_files_from_folder(folder_path, recursive=False):
    """Get all image files from a folder"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.psd', '.bmp']
    files = []
    
    if recursive:
        # Walk through all subdirectories
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    files.append(os.path.join(root, filename))
    else:
        # Only get files from the specified folder
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath) and any(filename.lower().endswith(ext) for ext in image_extensions):
                files.append(filepath)
    
    return files

def run_photoshop_script(jsx_file_path, photoshop_path=None):
    """Run a JSX script in Photoshop"""
    
    # Find Photoshop if path not provided
    if photoshop_path is None:
        photoshop_path = find_photoshop_path()
        if photoshop_path is None:
            print("Error: Could not find Photoshop installation.")
            print("Please specify the path manually using --ps-path argument")
            return False
    
    print(f"Using Photoshop: {photoshop_path}")
    print(f"Running script: {jsx_file_path}")
    
    try:
        # Run Photoshop with the script
        subprocess.run([photoshop_path, jsx_file_path], check=True)
        print("Script executed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Photoshop script: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Run Photoshop action on multiple files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process specific files
  python run_photoshop_action.py --jsx RunAction.jsx --files "C:\\images\\photo1.jpg" "C:\\images\\photo2.png"
  
  # Use wildcards to select files
  python run_photoshop_action.py --jsx RunAction.jsx --files "C:\\images\\*.jpg"
  
  # Process all images in a folder
  python run_photoshop_action.py --jsx RunAction.jsx --folder "C:\\images"
  
  # Process all images in a folder and subfolders
  python run_photoshop_action.py --jsx RunAction.jsx --folder "C:\\images" --recursive
  
  # With custom action and suffix
  python run_photoshop_action.py --jsx RunAction.jsx --files "image.jpg" --action-set "MyActions" --action "Resize" --suffix "_resized"
        '''
    )
    
    parser.add_argument('--jsx', required=True, help='Path to the JSX template file')
    
    # File input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--files', nargs='+', help='One or more file paths (supports wildcards like *.jpg)')
    input_group.add_argument('--folder', help='Process all image files in a folder')
    
    parser.add_argument('--recursive', action='store_true', help='Process subfolders recursively (only with --folder)')
    parser.add_argument('--action-set', help='Action set name (default: ABC)')
    parser.add_argument('--action', help='Action name (default: DFG)')
    parser.add_argument('--suffix', help='Suffix for output files (default: _applied)')
    parser.add_argument('--ps-path', help='Custom Photoshop executable path')
    
    args = parser.parse_args()
    
    # Check if template JSX exists
    if not os.path.exists(args.jsx):
        print(f"Error: JSX file not found: {args.jsx}")
        sys.exit(1)
    
    # Get list of files to process
    files_to_process = []
    
    if args.files:
        # Expand wildcards and validate files
        files_to_process = expand_file_patterns(args.files)
    elif args.folder:
        # Get all image files from folder
        if not os.path.exists(args.folder) or not os.path.isdir(args.folder):
            print(f"Error: Folder does not exist: {args.folder}")
            sys.exit(1)
        files_to_process = get_files_from_folder(args.folder, args.recursive)
    
    if not files_to_process:
        print("Error: No valid files found to process!")
        sys.exit(1)
    
    print(f"\nFound {len(files_to_process)} file(s) to process:")
    for i, file in enumerate(files_to_process[:10], 1):
        print(f"  {i}. {os.path.basename(file)}")
    if len(files_to_process) > 10:
        print(f"  ... and {len(files_to_process) - 10} more file(s)")
    
    # Create temporary JSX with specified files
    temp_jsx_path = create_jsx_with_files(
        args.jsx,
        files_to_process,
        action_set=args.action_set,
        action_name=args.action,
        suffix=args.suffix
    )
    
    if temp_jsx_path is None:
        sys.exit(1)
    
    try:
        # Run the script
        print("\nStarting Photoshop...")
        success = run_photoshop_script(temp_jsx_path, args.ps_path)
        sys.exit(0 if success else 1)
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_jsx_path)
        except:
            pass

if __name__ == "__main__":
    main()


# Usage
#  python run_photoshop_action.py --jsx RunAction.jsx --files "C:\images\photo1.jpg" "C:\images\photo2.png"
#  python run_photoshop_action.py --jsx RunAction.jsx --files "C:\images\*.jpg"
#  python run_photoshop_action.py --jsx RunAction.jsx --folder "C:\images"
#  python run_photoshop_action.py --jsx RunAction.jsx --folder "C:\images" --recursive
#  python run_photoshop_action.py --jsx RunAction.jsx --files "C:\folder1\image1.jpg" "D:\folder2\image2.png" "E:\photos\*.tif"
#  python run_photoshop_action.py --jsx RunAction.jsx --files "image.jpg" --action-set "MyActions" --action "Resize" --suffix "_resized"
#  MAC : python3 run_photoshop_action.py --jsx RunAction.jsx --files "/Users/me/photo1.jpg" "/Users/me/photo2.png"