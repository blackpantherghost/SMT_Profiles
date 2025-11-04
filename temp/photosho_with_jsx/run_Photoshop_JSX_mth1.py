#!/usr/bin/env python3
"""
Script to run Photoshop JSX scripts from command line
"""

import subprocess
import sys
import os
import platform

def run_photoshop_script(jsx_script_path, files=None, photoshop_path=None):
    """
    Execute a Photoshop JSX script
    
    Args:
        jsx_script_path (str): Path to the .jsx script file
        files (list): List of file paths to process
        photoshop_path (str): Custom path to Photoshop executable
    """
    
    # Default Photoshop paths based on OS
    if platform.system() == "Windows":
        default_ps_paths = [
            r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
            r"C:\Program Files\Adobe\Adobe Photoshop 2022\Photoshop.exe",
            r"C:\Program Files\Adobe\Adobe Photoshop 2021\Photoshop.exe",
            r"C:\Program Files\Adobe\Adobe Photoshop 2020\Photoshop.exe",
        ]
    elif platform.system() == "Darwin":  # macOS
        default_ps_paths = [
            "/Applications/Adobe Photoshop 2023/Adobe Photoshop 2023.app/Contents/MacOS/Adobe Photoshop 2023",
            "/Applications/Adobe Photoshop 2022/Adobe Photoshop 2022.app/Contents/MacOS/Adobe Photoshop 2022",
            "/Applications/Adobe Photoshop 2021/Adobe Photoshop 2021.app/Contents/MacOS/Adobe Photoshop 2021",
        ]
    else:
        print("Unsupported operating system")
        return False
    
    # Find Photoshop executable
    ps_exe = photoshop_path
    if not ps_exe:
        for path in default_ps_paths:
            if os.path.exists(path):
                ps_exe = path
                break
    
    if not ps_exe:
        print("Photoshop not found. Please specify the path manually.")
        return False
    
    if not os.path.exists(jsx_script_path):
        print(f"JSX script not found: {jsx_script_path}")
        return False
    
    # Prepare the JavaScript command
    js_command = f"""
    try {{
        // Load and execute the JSX script
        $.evalFile("{jsx_script_path.replace('\\\\', '\\\\\\\\')}");
    }} catch (e) {{
        alert("Error: " + e.toString());
    }}
    """
    
    # Write temporary JSX file that will load our target script
    temp_jsx = "temp_execute_script.jsx"
    with open(temp_jsx, 'w') as f:
        f.write(js_command)
    
    try:
        # Execute Photoshop with the script
        if platform.system() == "Windows":
            cmd = [ps_exe, temp_jsx]
        else:  # macOS
            cmd = [ps_exe, temp_jsx]
        
        print(f"Executing: {ps_exe} {temp_jsx}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Photoshop script executed successfully")
            return True
        else:
            print(f"Error executing Photoshop: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_jsx):
            os.remove(temp_jsx)

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) < 2:
        print("Usage: python run_photoshop_script.py <jsx_script> [--files file1 file2 ...] [--ps-path PATH]")
        print("Example: python run_photoshop_script.py RunAction.jsx --files C:\\images\\photo1.jpg C:\\images\\photo2.png")
        sys.exit(1)
    
    jsx_script = sys.argv[1]
    files = []
    ps_path = None
    
    # Parse command line arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--files":
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith("--"):
                files.append(sys.argv[i])
                i += 1
        elif sys.argv[i] == "--ps-path":
            i += 1
            if i < len(sys.argv):
                ps_path = sys.argv[i]
                i += 1
        else:
            i += 1
    
    # Run the Photoshop script
    success = run_photoshop_script(jsx_script, files, ps_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()