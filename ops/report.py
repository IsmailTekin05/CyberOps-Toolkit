import json
import os
import glob
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class ReportManager:
    def __init__(self, report_dir="../reports"):
        self.report_dir = report_dir

    def merge_reports(self):
        # masster_report = merge of all reports
        master_report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {}
        }

        # search for all JSON files in the report directory
        report_files = glob.glob(os.path.join(self.report_dir, "*.json"))

        for file_path in report_files:
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    master_report["summary"][file_name] = data
            except Exception as e:
                master_report["summary"][file_name] = f"Error reading log: {e}"

        return master_report

    def create_email_message(self, sender, recipient, subject, body):
        # creates an email message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        return msg.as_string()

    def send_smtp_raw(self, host, port, sender, recipient, message):
        try:
            with socket.create_connection((host, port), timeout=10) as sock:
                def send_cmd(cmd):
                    sock.sendall((cmd + "\r\n").encode())
                    return sock.recv(1024).decode()

                # Basic SMTP handshake
                send_cmd("HELO " + socket.gethostname())
                send_cmd(f"MAIL FROM:<{sender}>")
                send_cmd(f"RCPT TO:<{recipient}>")
                send_cmd("DATA")
                # SMTP ends the message with a single dot on a new line
                sock.sendall((message + "\r\n.\r\n").encode())
                send_cmd("QUIT")

                print(f"[*] Raw SMTP alert sent to {recipient}")
                return True
        except Exception as e:
            print(f"[-] Raw SMTP failed: {e}")
            return False

    def generate_executive_summary(self):
        # creates a human readable string from the merged JSON data
        data = self.merge_reports()
        summary_text = f"CyberSec Ops Toolkit - Executive Report\n"
        summary_text += f"Timestamp: {data['generated_at']}\n"
        summary_text += "=" * 40 + "\n"

        for tool, results in data["summary"].items():
            count = len(results) if isinstance(results, list) else "Data Present"
            summary_text += f"[+] Tool: {tool} | Entries: {count}\n"

        return summary_text