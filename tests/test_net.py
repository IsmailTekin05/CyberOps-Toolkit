import pytest
import os
import json
import tempfile
import threading

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ops.net import NetworkScanner


class TestNetworkScanner:

    @pytest.fixture
    def temp_dirs(self):
        with tempfile.TemporaryDirectory() as reports_dir:
            yield {'reports': reports_dir}

    @pytest.fixture
    def network_scanner(self, temp_dirs):
        log_file = os.path.join(temp_dirs['reports'], 'netscan_logs.json')
        scanner = NetworkScanner(
            target="192.168.1.0/30",
            ports=[22, 80, 443, 8080],
            timeout=1.0,
            max_threads=4,
            log_file=log_file
        )
        return scanner

    def test_initialization_sets_attributes(self, temp_dirs):
        log_file = os.path.join(temp_dirs['reports'], 'netscan_logs.json')
        scanner = NetworkScanner(
            target="10.0.0.0/24",
            ports=[22, 80, 443],
            timeout=2.0,
            max_threads=10,
            log_file=log_file
        )

        assert scanner.target == "10.0.0.0/24"
        assert scanner.ports == [22, 80, 443]
        assert scanner.timeout == 2.0
        assert scanner.max_threads == 10
        assert scanner.log_file == log_file

    def test_initialization_creates_log_directory(self, temp_dirs):
        log_file = os.path.join(temp_dirs['reports'], 'netscan_logs.json')
        scanner = NetworkScanner(
            target="192.168.1.1",
            ports=[22],
            log_file=log_file
        )

        assert os.path.exists(os.path.dirname(log_file))

    def test_initialization_initializes_results_list(self, network_scanner):
        assert network_scanner.results == []

    def test_initialization_creates_mutex_lock(self, network_scanner):
        assert isinstance(network_scanner.lock, threading.Lock)

    def test_initialization_with_default_timeout(self, temp_dirs):
        log_file = os.path.join(temp_dirs['reports'], 'netscan_logs.json')
        scanner = NetworkScanner(
            target="192.168.1.1",
            ports=[22]
        )

        assert scanner.timeout == 1.0

    def test_initialization_with_default_max_threads(self, temp_dirs):
        log_file = os.path.join(temp_dirs['reports'], 'netscan_logs.json')
        scanner = NetworkScanner(
            target="192.168.1.1",
            ports=[22]
        )

        assert scanner.max_threads == 50

    def test_log_finding_creates_log_file(self, network_scanner):
        network_scanner._log_finding("192.168.1.1", 22)

        assert os.path.exists(network_scanner.log_file)

    def test_log_finding_format(self, network_scanner):
        network_scanner._log_finding("192.168.1.1", 22)

        with open(network_scanner.log_file, 'r') as f:
            logs = json.load(f)

        assert len(logs) == 1
        entry = logs[0]
        assert 'timestamp' in entry
        assert entry['ip'] == "192.168.1.1"
        assert entry['port'] == 22
        assert entry['status'] == "open"

    def test_log_finding_appends_multiple_entries(self, network_scanner):
        network_scanner._log_finding("192.168.1.1", 22)
        network_scanner._log_finding("192.168.1.2", 80)
        network_scanner._log_finding("192.168.1.3", 443)

        with open(network_scanner.log_file, 'r') as f:
            logs = json.load(f)

        assert len(logs) == 3
        assert logs[0]['port'] == 22
        assert logs[1]['port'] == 80
        assert logs[2]['port'] == 443

    def test_log_finding_preserves_existing_logs(self, network_scanner):
        network_scanner._log_finding("192.168.1.1", 22)
        network_scanner._log_finding("192.168.1.2", 80)

        with open(network_scanner.log_file, 'r') as f:
            logs = json.load(f)

        assert len(logs) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
