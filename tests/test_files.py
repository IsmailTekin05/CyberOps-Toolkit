import pytest
import os
import tempfile

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ops.files import FileScanner

class TestFileScanner:

    @pytest.fixture
    def temp_dirs(self):
        with tempfile.TemporaryDirectory() as scan_dir:
            with tempfile.TemporaryDirectory() as quarantine_dir:
                with tempfile.TemporaryDirectory() as reports_dir:
                    yield {
                        'scan': scan_dir,
                        'quarantine': quarantine_dir,
                        'reports': reports_dir
                    }

    @pytest.fixture
    def file_scanner(self, temp_dirs):
        log_file = os.path.join(temp_dirs['reports'], 'scan_logs.json')
        scanner = FileScanner(
            scan_directory=temp_dirs['scan'],
            quarantine_directory=temp_dirs['quarantine'],
            log_file=log_file
        )
        return scanner

    def test_initialization_creates_directories(self, temp_dirs):
        log_file = os.path.join(temp_dirs['reports'], 'scan_logs.json')
        scanner = FileScanner(
            scan_directory=temp_dirs['scan'],
            quarantine_directory=temp_dirs['quarantine'],
            log_file=log_file
        )

        assert os.path.exists(scanner.quarantine_directory)
        assert os.path.exists(os.path.dirname(log_file))

    def test_initialization_compiles_patterns(self, file_scanner):
        assert len(file_scanner.compiled_patterns) == 4
        assert all(hasattr(p, 'search') for p in file_scanner.compiled_patterns)

    def test_initialization_sets_attributes(self, temp_dirs):
        log_file = os.path.join(temp_dirs['reports'], 'scan_logs.json')
        scanner = FileScanner(
            scan_directory=temp_dirs['scan'],
            quarantine_directory=temp_dirs['quarantine'],
            log_file=log_file
        )

        assert scanner.scan_directory == temp_dirs['scan']
        assert scanner.quarantine_directory == temp_dirs['quarantine']
        assert scanner.log_file == log_file

    def test_detect_eval_pattern(self, file_scanner, temp_dirs):
        test_file = os.path.join(temp_dirs['scan'], 'malicious.py')
        with open(test_file, 'w') as f:
            f.write('eval("dangerous code")')

        file_scanner._analyze_file(test_file)

        assert os.path.exists(os.path.join(temp_dirs['quarantine'], 'malicious.py'))

    def test_detect_base64_decode_pattern(self, file_scanner, temp_dirs):
        test_file = os.path.join(temp_dirs['scan'], 'encoded.php')
        with open(test_file, 'w') as f:
            f.write('$data = base64_decode($input);')

        file_scanner._analyze_file(test_file)

        assert os.path.exists(os.path.join(temp_dirs['quarantine'], 'encoded.php'))

    def test_detect_os_system_pattern(self, file_scanner, temp_dirs):
        test_file = os.path.join(temp_dirs['scan'], 'command.py')
        with open(test_file, 'w') as f:
            f.write('os.system("rm -rf /")')

        file_scanner._analyze_file(test_file)

        assert os.path.exists(os.path.join(temp_dirs['quarantine'], 'command.py'))

    def test_detect_powershell_pattern(self, file_scanner, temp_dirs):
        test_file = os.path.join(temp_dirs['scan'], 'script.ps1')
        with open(test_file, 'w') as f:
            f.write('powershell.exe -Enc JABhID0gMQ==')

        file_scanner._analyze_file(test_file)

        assert os.path.exists(os.path.join(temp_dirs['quarantine'], 'script.ps1'))

    def test_pattern_case_insensitive(self, file_scanner, temp_dirs):
        test_file = os.path.join(temp_dirs['scan'], 'uppercase.py')
        with open(test_file, 'w') as f:
            f.write('EVAL("code")')

        file_scanner._analyze_file(test_file)

        assert os.path.exists(os.path.join(temp_dirs['quarantine'], 'uppercase.py'))

    def test_no_detection_for_clean_file(self, file_scanner, temp_dirs):
        test_file = os.path.join(temp_dirs['scan'], 'clean.py')
        with open(test_file, 'w') as f:
            f.write('def hello():\n    print("Hello World")')

        file_scanner._analyze_file(test_file)

        assert not os.path.exists(os.path.join(temp_dirs['quarantine'], 'clean.py'))
        assert os.path.exists(test_file)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])