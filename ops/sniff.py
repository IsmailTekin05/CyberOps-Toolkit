import re
import json
from datetime import datetime
from scapy.all import sniff
from scapy.layers.inet import IP, TCP
from scapy.packet import Raw


class PacketSniffer:
    def __init__(self, interface=None, log_file="../reports/sniff_stats.json"):
        self.interface = interface
        self.log_file = log_file

        self.stats = {
            "total_packets_analyzed": 0,
            "credentials_detected": 0,
            "start_time": datetime.now().isoformat()
        }

        #patterns for credentials
        self.credential_patterns = [
            #username or email
            re.compile(r"(?i)(?:user|username|login|email)\s*=\s*([^&\s]+)"),
            #password
            re.compile(r"(?i)(?:password|pass|pwd)\s*=\s*([^&\s]+)"),
            #authorization header or token
            re.compile(r"(?i)Authorization:\s*Basic\s*([a-zA-Z0-9+=]+)")
        ]

    def _update_log(self, source_ip, dest_ip, matched_data, match_type):
        self.stats["credentials_detected"] += 1

        entry = {
            "timestamp": datetime.now().isoformat(),
            "source_ip": source_ip,
            "destination_ip": dest_ip,
            "type": match_type,
            "data": matched_data
        }

        data_store = {"statistics": self.stats, "findings": []}

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                if "findings" in content:
                    data_store["findings"] = content["findings"]
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        data_store["findings"].append(entry)
        data_store["statistics"] = self.stats

        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(data_store, f, indent=4)

    def _process_packet(self, packet):
        #checks before processing the data
        if packet.haslayer(TCP) and packet.haslayer(Raw) and packet.haslayer(IP):
            self.stats["total_packets_analyzed"] += 1

            #if we found a packet that has credentials we log that
            try:
                payload = packet[Raw].load.decode("utf-8", errors="ignore")

                if "HTTP" in payload or "POST" in payload or "GET" in payload:
                    for pattern in self.credential_patterns:
                        matches = pattern.findall(payload)
                        for match in matches:
                            self._update_log(packet[IP].src, packet[IP].dst, match, pattern.pattern)
            except Exception:
                pass

    def start(self, packet_count=0):
        #start to sniff using scapy
        try:
            #iface = interface to listen, prn = first function gets called after capturing a packet and we use it for
            #processing raw data, store = asks for storing data on ram and we already log it so no need and it could lead
            #to unsafe memory issues, count = number of packets sniff should caught before closing.
            sniff(iface=self.interface, prn=self._process_packet, store=False, count=packet_count)
        except KeyboardInterrupt:
            print("\n[*] Capture stopped by user.")
        finally:
            print(f"[*] Sniffing complete. Total packets analyzed: {self.stats['total_packets_analyzed']}")
            print(f"[*] Credentials found: {self.stats['credentials_detected']}")