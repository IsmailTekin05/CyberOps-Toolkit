import argparse
from ops.files import FileScanner
from ops.net import NetworkScanner
from ops.sniff import PacketSniffer
from ops.scrape import WebScraper
from ops.web_auto import BrowserAutomator
from ops.ssh import CommandExecutor
from ops.serve import ReportServer
from ops.report import ReportManager

def main_cli():
    parser = argparse.ArgumentParser(description="CyberSec Ops Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Available Tools")

    scan_parser = subparsers.add_parser("scan", help="File Scanner")
    scan_parser.add_argument("--dir", required=True, help="Directory to scan")
    scan_parser.add_argument("--ext", default="*", help="File extension filter")

    net_parser = subparsers.add_parser("net-scan", help="Network Port Scanner")
    net_parser.add_argument("--target", required=True, help="Target IP or CIDR")
    net_parser.add_argument("--ports", type=int, nargs="+", required=True, help="Ports to scan")
    net_parser.add_argument("--threads", type=int, default=50)

    sniff_parser = subparsers.add_parser("sniff", help="Packet Sniffer")
    sniff_parser.add_argument("--iface", help="Network interface")
    sniff_parser.add_argument("--count", type=int, default=0)

    scrape_parser = subparsers.add_parser("scrape", help="Web Scraper")
    scrape_parser.add_argument("--url", required=True)
    scrape_parser.add_argument("--selectors", nargs="+", help="CSS Selectors")

    auto_parser = subparsers.add_parser("web-auto", help="Selenium Automation")
    auto_parser.add_argument("--url", required=True)

    ssh_parser = subparsers.add_parser("ssh", help="SSH Executor")
    ssh_parser.add_argument("--host", required=True)
    ssh_parser.add_argument("--user", required=True)
    ssh_parser.add_argument("--cmd", required=True)
    ssh_parser.add_argument("--pwd", help="Password")

    serve_parser = subparsers.add_parser("serve", help="Start Dashboard")
    serve_parser.add_argument("--port", type=int, default=8080)

    report_parser = subparsers.add_parser("report", help="Generate/Send Report")
    report_parser.add_argument("--email", help="Recipient email for alert")

    args = parser.parse_args()

    if args.command == "scan":
        scanner = FileScanner(args.dir)
        scanner.scan(args.ext)

    elif args.command == "net-scan":
        scanner = NetworkScanner(args.target, args.ports, max_threads=args.threads)
        scanner.scan()

    elif args.command == "sniff":
        sniffer = PacketSniffer(interface=args.iface)
        sniffer.start(packet_count=args.count)

    elif args.command == "scrape":
        scraper = WebScraper(args.url, selectors=args.selectors)
        scraper.scrape()

    elif args.command == "web-auto":
        automator = BrowserAutomator()
        automator.capture_screenshot(args.url)
        automator.close()

    elif args.command == "ssh":
        executor = CommandExecutor()
        executor.execute_remote(args.host, args.user, args.cmd, password=args.pwd)

    elif args.command == "serve":
        server = ReportServer(port=args.port)
        server.start()

    elif args.command == "report":
        reporter = ReportManager()
        summary = reporter.generate_executive_summary()
        print(summary)
        if args.email:
            msg = reporter.create_email_message("toolkit@ops.local", args.email, "Security Report", summary)
            reporter.send_smtp_raw("localhost", 25, "toolkit@ops.local", args.email, msg)

    else:
        parser.print_help()