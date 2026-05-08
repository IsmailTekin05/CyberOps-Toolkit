import os
import json
import socket
import threading
import random
import time
import itertools
import ipaddress
from datetime import datetime
from ops.utils import ensure_dir


class NetworkScanner:
    # target = target ip, ports = a list of ports, timeout = timeout duration for scanning, max_threads = max thread count
    def __init__(self, target, ports, timeout=1.0, max_threads=50, log_file="../reports/netscan_logs.json"):
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.max_threads = max_threads
        self.log_file = log_file
        self.results = []
        # mutex lock
        self.lock = threading.Lock()

        ensure_dir(log_file)

    def _log_finding(self, ip, port):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": str(ip),
            "port": port,
            "status": "open"
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

    # check if the ip address and port is open
    def _scan_target(self, ip, port):
        # connect to socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        # checks for existing connection
        try:
            result = sock.connect_ex((str(ip), port))
            if result == 0:
                # if the mutex lock is open then get in lock the mutex and append the result then release the key
                with self.lock:
                    self.results.append({"ip": str(ip), "port": port, "status": "open"})
                    self._log_finding(ip, port)
        except Exception:
            pass
        finally:
            sock.close()

    # calls the _scan_target for every ip-port pair
    def _worker(self, tasks):
        for ip, port in tasks:
            self._scan_target(ip, port)
            time.sleep(random.uniform(0.01, 0.1))

    def scan(self):
        # prepares the possible ip address
        try:
            network = ipaddress.ip_network(self.target, strict=False)
            hosts = list(network.hosts())
            if not hosts:
                hosts = [ipaddress.ip_address(self.target)]
        except ValueError:
            hosts = [self.target]

        scan_list = list(itertools.product(hosts, self.ports))
        random.shuffle(scan_list)

        # create the threads
        threads = []
        tasks_per_thread = max(1, len(scan_list) // self.max_threads)

        # distribute the ip address to threads
        tasks_split = [scan_list[i:i + tasks_per_thread] for i in range(0, len(scan_list), tasks_per_thread)]

        # initialize the threads
        for task_chunk in tasks_split:
            thread = threading.Thread(target=self._worker, args=(task_chunk,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return self.results