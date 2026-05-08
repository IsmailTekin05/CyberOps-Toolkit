import os
import re
import json
import shutil
from datetime import datetime
import send2trash
import glob
import fnmatch
from ops.utils import ensure_dir

class FileScanner:
    #Initializes the class with directory to scan, a quarantine directory path and log files path
    def __init__(self, scan_directory, quarantine_directory="../reports/quarantine", log_file="../reports/scan_logs.json"):
        self.scan_directory = scan_directory
        self.quarantine_directory = quarantine_directory
        self.log_file = log_file

        #Checks if the given quarantine dir exists if not creates it
        if not os.path.exists(self.quarantine_directory):
            os.makedirs(self.quarantine_directory)

        #Checks if log dir is valid and if not exists creates it
        ensure_dir(log_file)

        self.suspicious_patterns = [
            r"eval\s*\(",
            r"base64_decode\s*\(",
            r"os\.system\s*\(",
            r"powershell.*-Enc"
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]

    #logs the results
    def log_finding(self, file_path, reason):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "reason": reason,
            "action": "quarantined"
        }
        
        logs = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    pass
                    
        logs.append(log_entry)
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

    #quarantines the given file_path with send2trash
    def quarantine(self, file_path, use_trash=True):
        try:
            if use_trash:
                send2trash.send2trash(file_path)
            else:
                file_name = os.path.basename(file_path)
                destination = os.path.join(self.quarantine_directory, file_name)
                shutil.move(file_path, destination)
            return True
        except Exception as e:
            print(f"[!] Error quarantining {file_path}: {e}")
            return False

    #looks for suspicious files with and if finds it any, analyzes it
    def scan(self, file_extension="*"):
        search_pattern = os.path.join(self.scan_directory, "**", "*")
        for file_path in glob.iglob(search_pattern, recursive=True):
            if os.path.isfile(file_path):
                if fnmatch.fnmatch(os.path.basename(file_path), file_extension):
                    self._analyze_file(file_path)

    #checks if the given file has matching text with suspicious_patterns with regex
    def _analyze_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
                for pattern in self.compiled_patterns:
                    match = pattern.search(content)
                    if match:
                        if self.quarantine(file_path, use_trash=False):
                            self.log_finding(file_path, f"Regex match: {pattern.pattern}")
                        break
        except Exception as e:
            print(f"[-] Could not read {file_path}: {e}")
