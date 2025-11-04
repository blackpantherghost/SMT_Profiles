#!/usr/bin/env python3
"""
Advanced Photoshop JSX script runner with better argument handling
"""

import subprocess
import sys
import os
import platform
import json
import tempfile

class PhotoshopScriptRunner:
    def __init__(self, photoshop_path=None):
        self.photoshop_path = photoshop_path or self.find_photoshop()
    
    def find_photoshop(self):
        """Find Photoshop installation path"""
        if platform.system() == "Windows":
            paths = [
                r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
                r"C:\Program Files\Adobe\Adobe Photoshop 2022\Photoshop.exe",
                r"C:\Program Files\Adobe\Adobe Photoshop 2021\Photoshop.exe",
            ]
        elif platform.system() == "Darwin":
            paths = [
                "/Applications/Adobe Photoshop 2023/Adobe Photoshop 2023.app/Contents/MacOS/Adobe Photoshop 2023",
                "/Applications/Adobe Photoshop 2022/Adobe Photoshop 2022.app/Contents/MacOS/Adobe Photoshop 2022",
            ]
        else:
            return None
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def create_wrapper_script(self, target_script, files):
        """Create a wrapper JSX script that passes arguments to the target script"""
        
        # Convert files list to JavaScript array
        files_js = "[" + ", ".join([f'"{f.replace("\\\\", "\\\\\\\\")}"' for f in files]) + "]"
        
        wrapper_script = f"""
// Wrapper script to execute {target_script} with arguments
var scriptArgs = {{
    files: {files_js}
}};

// Store arguments in global variable for the target script to access
$.global.scriptArgs = scriptArgs;

// Execute the target script
try {{
    $.evalFile("{target_script.replace('\\\\', '\\\\\\\\')}");
    // Force Photoshop to close after execution (optional)
    // app.quit();
}} catch (e) {{
    alert("Error executing script: " + e.toString());
}}
"""
        return wrapper_script
    
    def run_script(self, jsx_script_path, files=None):
        """Execute Photoshop JSX script with file arguments"""
        
        if not self.photoshop_path:
            print("Error: Photoshop not found. Please specify the path using --ps-path")
            return False
        
        if not os.path.exists(jsx_script_path):
            print(f"Error: JSX script not found: {jsx_script_path}")
            return False
        
        files = files or []
        
        # Create temporary wrapper script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsx', delete=False) as temp_file:
            wrapper_content = self.create_wrapper_script(jsx_script_path, files)
            temp_file.write(wrapper_content)
            temp_script_path = temp_file.name
        
        try:
            # Execute Photoshop
            if platform.system() == "Windows":
                cmd = [self.photoshop_path, temp_script_path]
            else:
                cmd = [self.photoshop_path, temp_script_path]
            
            print(f"Running Photoshop script: {jsx_script_path}")
            print(f"Files to process: {files}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✓ Photoshop script executed successfully")
                return True
            else:
                print(f"✗ Error executing Photoshop: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Photoshop execution timed out")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
        finally:
            # Clean up temporary file
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)

def main():
    """Command line interface"""
    
    if len(sys.argv) < 2:
        print("Photoshop JSX Script Runner")
        print("=" * 50)
        print("Usage: python run_ps_script.py <script.jsx> [OPTIONS]")
        print("\nOptions:")
        print("  --files FILE1 FILE2 ...    Files to process")
        print("  --ps-path PATH            Custom Photoshop executable path")
        print("  --help                    Show this help message")
        print("\nExample:")
        print('  python run_ps_script.py RunAction.jsx --files "C:\\images\\photo1.jpg" "C:\\images\\photo2.png"')
        sys.exit(1)
    
    if sys.argv[1] == "--help":
        main()  # This will show the help message above
        return
    
    jsx_script = sys.argv[1]
    files = []
    ps_path = None
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--files":
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith("--"):
                if os.path.exists(sys.argv[i]):
                    files.append(os.path.abspath(sys.argv[i]))
                else:
                    print(f"Warning: File not found: {sys.argv[i]}")
                i += 1
        elif sys.argv[i] == "--ps-path":
            i += 1
            if i < len(sys.argv):
                ps_path = sys.argv[i]
                if not os.path.exists(ps_path):
                    print(f"Error: Photoshop not found at: {ps_path}")
                    sys.exit(1)
                i += 1
        else:
            print(f"Warning: Unknown argument: {sys.argv[i]}")
            i += 1
    
    # Initialize and run
    runner = PhotoshopScriptRunner(ps_path)
    success = runner.run_script(jsx_script, files)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()