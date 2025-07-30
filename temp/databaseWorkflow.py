# Simple Shared Database Logging System

## Architecture Overview

```
Desktop Apps → Shared Network Path → SQLite Database + User Authentication File
```

## 1. Server Setup Structure

```
\\server\shared_app_logs\
├── users.db                 # User authentication database
├── app_logs.db             # Main application logs database  
├── config.ini              # Configuration file
└── logs\                   # Backup log files (optional)
    ├── 2025-07-30.log
    └── archive\
```

## 2. Implementation Files

### Project Structure
```
your_app/
├── main.py
├── database/
│   ├── __init__.py
│   ├── db_manager.py       # Database operations
│   └── auth_db.py          # User authentication
├── logging/
│   ├── __init__.py
│   └── app_logger.py       # Logging functionality
├── utils/
│   ├── __init__.py
│   ├── machine_info.py     # Get system information
│   └── file_lock.py        # File locking for concurrent access
└── gui/
    ├── __init__.py
    └── main_window.py      # Simple GUI
```

## 3. Database Schema

### database/db_manager.py
```python
import sqlite3
import threading
import time
import os
from datetime import datetime
from utils.file_lock import FileLock

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.users_db_path = os.path.join(os.path.dirname(db_path), "users.db")
        self.lock = threading.Lock()
        self._init_databases()
    
    def _init_databases(self):
        """Initialize both user authentication and logging databases"""
        # Create users database
        self._create_users_db()
        # Create logs database
        self._create_logs_db()
    
    def _create_users_db(self):
        """Create users authentication database"""
        conn = sqlite3.connect(self.users_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                department TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Insert default admin user if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO authorized_users (username, full_name, department)
            VALUES ('admin', 'Administrator', 'IT')
        ''')
        
        conn.commit()
        conn.close()
    
    def _create_logs_db(self):
        """Create application logs database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                username TEXT NOT NULL,
                machine_name TEXT NOT NULL,
                machine_details TEXT,
                function_name TEXT,
                module_name TEXT,
                log_level TEXT DEFAULT 'INFO',
                message TEXT,
                execution_time_ms REAL,
                success BOOLEAN DEFAULT TRUE,
                error_details TEXT,
                session_id TEXT,
                app_version TEXT
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON app_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON app_logs(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_machine ON app_logs(machine_name)')
        
        conn.commit()
        conn.close()
    
    def authenticate_user(self, username):
        """Check if user is authorized"""
        try:
            with FileLock(self.users_db_path + ".lock"):
                conn = sqlite3.connect(self.users_db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT username, full_name, is_active 
                    FROM authorized_users 
                    WHERE username = ? AND is_active = TRUE
                ''', (username,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    # Update last login
                    self._update_last_login(username)
                    return True, {"username": result[0], "full_name": result[1]}
                else:
                    return False, "User not authorized or inactive"
                    
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    
    def _update_last_login(self, username):
        """Update user's last login timestamp"""
        try:
            with FileLock(self.users_db_path + ".lock"):
                conn = sqlite3.connect(self.users_db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE authorized_users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE username = ?
                ''', (username,))
                conn.commit()
                conn.close()
        except:
            pass  # Non-critical operation
    
    def add_log_entry(self, log_data):
        """Add a log entry to the database with file locking"""
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with FileLock(self.db_path + ".lock", timeout=5):
                    conn = sqlite3.connect(self.db_path, timeout=10.0)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO app_logs (
                            timestamp, username, machine_name, machine_details,
                            function_name, module_name, log_level, message,
                            execution_time_ms, success, error_details,
                            session_id, app_version
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        log_data.get('timestamp', datetime.now().isoformat()),
                        log_data.get('username'),
                        log_data.get('machine_name'),
                        log_data.get('machine_details'),
                        log_data.get('function_name'),
                        log_data.get('module_name'),
                        log_data.get('log_level', 'INFO'),
                        log_data.get('message'),
                        log_data.get('execution_time_ms'),
                        log_data.get('success', True),
                        log_data.get('error_details'),
                        log_data.get('session_id'),
                        log_data.get('app_version')
                    ))
                    
                    conn.commit()
                    conn.close()
                    return True
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    print(f"Failed to add log entry after {max_retries} attempts: {e}")
                    return False
        
        return False
    
    def get_logs(self, username=None, machine_name=None, limit=100, offset=0):
        """Retrieve logs with optional filtering"""
        try:
            with FileLock(self.db_path + ".lock"):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                query = "SELECT * FROM app_logs WHERE 1=1"
                params = []
                
                if username:
                    query += " AND username = ?"
                    params.append(username)
                
                if machine_name:
                    query += " AND machine_name = ?"
                    params.append(machine_name)
                
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                conn.close()
                
                # Convert to list of dictionaries
                logs = []
                for row in results:
                    logs.append(dict(zip(columns, row)))
                
                return logs
                
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return []
    
    def add_authorized_user(self, username, full_name, department):
        """Add a new authorized user (admin function)"""
        try:
            with FileLock(self.users_db_path + ".lock"):
                conn = sqlite3.connect(self.users_db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO authorized_users (username, full_name, department)
                    VALUES (?, ?, ?)
                ''', (username, full_name, department))
                
                conn.commit()
                conn.close()
                return True
                
        except sqlite3.IntegrityError:
            return False  # User already exists
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
```

## 4. File Locking Utility

### utils/file_lock.py
```python
import os
import time
import errno
import tempfile

class FileLock:
    """Simple file-based locking mechanism for concurrent access"""
    
    def __init__(self, lock_file_path, timeout=30):
        self.lock_file_path = lock_file_path
        self.timeout = timeout
        self.lock_file = None
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
    
    def acquire(self):
        """Acquire the file lock"""
        start_time = time.time()
        
        while True:
            try:
                # Try to create lock file exclusively
                self.lock_file = os.open(
                    self.lock_file_path,
                    os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                
                # Write process ID to lock file
                os.write(self.lock_file, str(os.getpid()).encode())
                return True
                
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                
                # Check if we've exceeded timeout
                if time.time() - start_time >= self.timeout:
                    raise TimeoutError(f"Could not acquire lock within {self.timeout} seconds")
                
                # Wait a bit before retrying
                time.sleep(0.1)
    
    def release(self):
        """Release the file lock"""
        if self.lock_file:
            try:
                os.close(self.lock_file)
                os.unlink(self.lock_file_path)
            except:
                pass  # Lock file might have been removed already
            finally:
                self.lock_file = None
```

## 5. Machine Information Utility

### utils/machine_info.py
```python
import socket
import platform
import getpass
import json

def get_machine_details():
    """Get comprehensive machine information"""
    try:
        import psutil
        memory_info = f"{psutil.virtual_memory().total // (1024**3)}GB"
        cpu_count = psutil.cpu_count()
    except ImportError:
        memory_info = "Unknown"
        cpu_count = "Unknown"
    
    details = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "current_user": getpass.getuser(),
        "total_memory": memory_info,
        "cpu_count": cpu_count
    }
    
    return json.dumps(details)

def get_machine_name():
    """Get simple machine name"""
    return socket.gethostname()

def get_current_username():
    """Get current logged-in username"""
    return getpass.getuser()
```

## 6. Application Logger

### logging/app_logger.py
```python
import logging
import uuid
from datetime import datetime
from database.db_manager import DatabaseManager
from utils.machine_info import get_machine_details, get_machine_name, get_current_username

class AppLogger:
    def __init__(self, db_path, app_version="1.0.0"):
        self.db_manager = DatabaseManager(db_path)
        self.app_version = app_version
        self.session_id = str(uuid.uuid4())
        self.current_user = None
        self.authenticated = False
    
    def authenticate(self, username=None):
        """Authenticate user for logging"""
        if username is None:
            username = get_current_username()
        
        success, result = self.db_manager.authenticate_user(username)
        
        if success:
            self.current_user = result
            self.authenticated = True
            self.log_info("User authenticated successfully", "AUTH")
            return True, f"Welcome {result['full_name']}"
        else:
            self.authenticated = False
            return False, result
    
    def log_function_call(self, function_name, module_name, message, 
                         execution_time_ms=None, success=True, error_details=None):
        """Log a function call"""
        if not self.authenticated:
            return False
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'username': self.current_user['username'],
            'machine_name': get_machine_name(),
            'machine_details': get_machine_details(),
            'function_name': function_name,
            'module_name': module_name,
            'log_level': 'ERROR' if not success else 'INFO',
            'message': message,
            'execution_time_ms': execution_time_ms,
            'success': success,
            'error_details': error_details,
            'session_id': self.session_id,
            'app_version': self.app_version
        }
        
        return self.db_manager.add_log_entry(log_data)
    
    def log_info(self, message, function_name="GENERAL"):
        """Log an info message"""
        return self.log_function_call(function_name, "APP", message)
    
    def log_error(self, message, function_name="ERROR", error_details=None):
        """Log an error message"""
        return self.log_function_call(function_name, "APP", message, 
                                    success=False, error_details=error_details)
    
    def get_logs(self, **kwargs):
        """Retrieve logs from database"""
        return self.db_manager.get_logs(**kwargs)

# Decorator for automatic function logging
def log_function(logger):
    """Decorator factory that takes logger instance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                logger.log_function_call(
                    function_name=func.__name__,
                    module_name=func.__module__,
                    message=f"Function {func.__name__} executed successfully",
                    execution_time_ms=execution_time,
                    success=True
                )
                
                return result
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                logger.log_function_call(
                    function_name=func.__name__,
                    module_name=func.__module__,
                    message=f"Function {func.__name__} failed: {str(e)}",
                    execution_time_ms=execution_time,
                    success=False,
                    error_details=str(e)
                )
                raise
        
        return wrapper
    return decorator
```

## 7. Simple GUI Application

### gui/main_window.py
```python
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from logging.app_logger import AppLogger, log_function

class MainWindow:
    def __init__(self, db_path):
        self.db_path = db_path
        self.logger = AppLogger(db_path)
        self.root = tk.Tk()
        self.setup_ui()
        self.authenticate_user()
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.root.title("Application with Logging")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # User info frame
        user_frame = ttk.LabelFrame(main_frame, text="User Information", padding="5")
        user_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.user_label = ttk.Label(user_frame, text="Not authenticated")
        self.user_label.grid(row=0, column=0)
        
        # Function buttons frame
        buttons_frame = ttk.LabelFrame(main_frame, text="Application Functions", padding="5")
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        ttk.Button(buttons_frame, text="Process Data", 
                  command=self.process_data).grid(row=0, column=0, pady=2, sticky=tk.W+tk.E)
        ttk.Button(buttons_frame, text="Generate Report", 
                  command=self.generate_report).grid(row=1, column=0, pady=2, sticky=tk.W+tk.E)
        ttk.Button(buttons_frame, text="Export Files", 
                  command=self.export_files).grid(row=2, column=0, pady=2, sticky=tk.W+tk.E)
        ttk.Button(buttons_frame, text="Calculate Results", 
                  command=self.calculate_results).grid(row=3, column=0, pady=2, sticky=tk.W+tk.E)
        
        # Logs display frame
        logs_frame = ttk.LabelFrame(main_frame, text="Recent Logs", padding="5")
        logs_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, width=50, height=20)
        self.logs_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Button(logs_frame, text="Refresh Logs", 
                  command=self.refresh_logs).grid(row=1, column=0, pady=(5, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
    
    def authenticate_user(self):
        """Authenticate the current user"""
        success, message = self.logger.authenticate()
        
        if success:
            self.user_label.config(text=f"Logged in as: {message}")
            self.refresh_logs()
        else:
            messagebox.showerror("Authentication Failed", message)
            self.root.quit()
    
    @log_function
    def process_data(self):
        """Example function 1 - automatically logged"""
        import time
        import random
        
        # Simulate processing
        time.sleep(random.uniform(0.5, 2.0))
        
        messagebox.showinfo("Success", "Data processed successfully!")
        self.refresh_logs()
    
    @log_function  
    def generate_report(self):
        """Example function 2 - automatically logged"""
        import time
        import random
        
        # Simulate report generation
        time.sleep(random.uniform(1.0, 3.0))
        
        if random.choice([True, False, True, True]):  # 75% success rate
            messagebox.showinfo("Success", "Report generated successfully!")
        else:
            raise Exception("Report generation failed due to missing data")
        
        self.refresh_logs()
    
    @log_function
    def export_files(self):
        """Example function 3 - automatically logged"""
        import time
        
        time.sleep(1.5)
        messagebox.showinfo("Success", "Files exported successfully!")
        self.refresh_logs()
    
    @log_function
    def calculate_results(self):
        """Example function 4 - automatically logged"""
        import time
        import random
        
        time.sleep(random.uniform(0.8, 2.5))
        
        if random.choice([True, True, True, False]):  # 75% success rate
            messagebox.showinfo("Success", "Calculations completed!")
        else:
            raise Exception("Calculation error: Division by zero")
        
        self.refresh_logs()
    
    def refresh_logs(self):
        """Refresh the logs display"""
        logs = self.logger.get_logs(limit=20)
        
        self.logs_text.delete(1.0, tk.END)
        
        for log in logs:
            status = "✓" if log['success'] else "✗"
            timestamp = log['timestamp'][:19]  # Remove microseconds
            log_line = f"{status} {timestamp} | {log['function_name']} | {log['message']}\n"
            self.logs_text.insert(tk.END, log_line)
        
        self.logs_text.see(tk.END)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Apply the decorator to the class methods
def apply_logging_decorator(cls, logger_instance):
    """Apply logging decorator to class methods"""
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_') and attr_name not in ['run', 'setup_ui', 'authenticate_user', 'refresh_logs']:
            setattr(cls, attr_name, log_function(logger_instance)(attr))

# Modify the __init__ method to apply decorators
def modified_init(self, db_path):
    self.db_path = db_path
    self.logger = AppLogger(db_path)
    
    # Apply logging decorators to methods
    for method_name in ['process_data', 'generate_report', 'export_files', 'calculate_results']:
        method = getattr(self, method_name)
        setattr(self, method_name, log_function(self.logger)(method))
    
    self.root = tk.Tk()
    self.setup_ui()
    self.authenticate_user()

# Replace the original __init__ method
MainWindow.__init__ = modified_init
```

## 8. Main Application Entry Point

### main.py
```python
import os
import sys
from gui.main_window import MainWindow

def main():
    # Configuration
    SERVER_PATH = r"\\your-server\shared_app_logs"  # Modify this path
    DB_PATH = os.path.join(SERVER_PATH, "app_logs.db")
    
    # Check if server path is accessible
    if not os.path.exists(SERVER_PATH):
        print(f"Error: Cannot access server path: {SERVER_PATH}")
        print("Please check:")
        print("1. Network connectivity")
        print("2. Server path permissions")
        print("3. Path spelling")
        input("Press Enter to exit...")
        sys.exit(1)
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(SERVER_PATH, exist_ok=True)
        
        # Start the application
        app = MainWindow(DB_PATH)
        app.run()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
```

## 9. User Management Script

### admin_tools.py
```python
from database.db_manager import DatabaseManager
import os

def add_users():
    """Script to add authorized users"""
    SERVER_PATH = r"\\your-server\shared_app_logs"
    DB_PATH = os.path.join(SERVER_PATH, "app_logs.db")
    
    db_manager = DatabaseManager(DB_PATH)
    
    # Add sample users
    users_to_add = [
        ("john.doe", "John Doe", "Engineering"),
        ("jane.smith", "Jane Smith", "Quality Assurance"),
        ("mike.wilson", "Mike Wilson", "Production"),
        ("sarah.jones", "Sarah Jones", "Management")
    ]
    
    for username, full_name, department in users_to_add:
        success = db_manager.add_authorized_user(username, full_name, department)
        if success:
            print(f"Added user: {username}")
        else:
            print(f"Failed to add user: {username} (might already exist)")

if __name__ == "__main__":
    add_users()
```

## 10. Building the Executable

### build.py
```python
import PyInstaller.__main__
import os

# Build the application
PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=MyApp',
    '--add-data=database;database',
    '--add-data=logging;logging',
    '--add-data=utils;utils',
    '--add-data=gui;gui',
    '--hidden-import=sqlite3',
    '--hidden-import=tkinter',
    '--distpath=dist'
])

print("Build complete! Executable is in the 'dist' folder.")
```

## 11. Configuration File

### config.ini
```ini
[DATABASE]
server_path = \\your-server\shared_app_logs
database_name = app_logs.db
users_database_name = users.db

[APPLICATION]
app_name = My Application
app_version = 1.0.0
log_level = INFO

[SECURITY]
max_lock_timeout = 30
retry_attempts = 5
```

This simplified approach provides:

1. **File-based authentication** using SQLite database on shared server path
2. **Concurrent access handling** using file locks
3. **Automatic logging** of function calls with decorators  
4. **Simple user management** through admin scripts
5. **Standalone executable** that works across the network
6. **Real-time log viewing** in the application

The system is much simpler than a full web API approach while still providing robust logging and user authentication capabilities.