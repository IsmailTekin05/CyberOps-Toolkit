import http.server
import socketserver
import os


class ReportServer:
    # report_dir = path to your json and image reports, port = local port to bind
    def __init__(self, report_dir="../reports", port=8080):
        self.report_dir = os.path.abspath(report_dir)
        self.port = port

    def start(self):
        if not os.path.exists(self.report_dir):
            return

        # Change the working directory of the process to the reports folder
        os.chdir(self.report_dir)

        handler = http.server.SimpleHTTPRequestHandler

        # allow address to reuse to prevent errors
        socketserver.TCPServer.allow_reuse_address = True

        try:
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Stopping the HTTP Dashboard.")
        except Exception as e:
            print(f"[-] Server error: {e}")