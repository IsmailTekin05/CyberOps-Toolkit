import os
import json
import subprocess
import paramiko
from datetime import datetime
from ops.utils import ensure_dir


class CommandExecutor:
    def __init__(self, log_file="../reports/execution_logs.json"):
        self.log_file = log_file

        ensure_dir(log_file)

    def _log_execution(self, target, command, status, output):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "command": command,
            "status": status,
            "output": output.strip() if output else ""
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

    #runs the command in my host machine
    def execute_local(self, command):
        try:
            #runs the command on shell, saves the output and sets a time limit to 30 seconds
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            #checks if the output is valid or not
            output = result.stdout if result.returncode == 0 else result.stderr
            status = "success" if result.returncode == 0 else "error"

            self._log_execution("localhost", command, status, output)
            return {"status": status, "output": output}

        except subprocess.TimeoutExpired:
            error_msg = "Command execution timed out after 30 seconds."
            self._log_execution("localhost", command, "timeout", error_msg)
            return {"status": "timeout", "output": error_msg}
        except Exception as e:
            self._log_execution("localhost", command, "exception", str(e))
            return {"status": "exception", "output": str(e)}

    def execute_remote(self, host, username, command, password=None, key_file=None):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(
                hostname=host,
                username=username,
                password=password,
                key_filename=key_file,
                timeout=10
            )

            #executes the code
            stdin, stdout, stderr = client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            #decodes the responses
            out_text = stdout.read().decode("utf-8", errors="ignore")
            err_text = stderr.read().decode("utf-8", errors="ignore")

            #checks if the response is valid
            final_output = out_text if exit_status == 0 else err_text
            status = "success" if exit_status == 0 else "error"

            self._log_execution(host, command, status, final_output)
            return {"status": status, "output": final_output}

        except paramiko.AuthenticationException:
            error_msg = "Authentication failed."
            self._log_execution(host, command, "auth_error", error_msg)
            return {"status": "auth_error", "output": error_msg}
        except Exception as e:
            self._log_execution(host, command, "exception", str(e))
            return {"status": "exception", "output": str(e)}
        finally:
            client.close()