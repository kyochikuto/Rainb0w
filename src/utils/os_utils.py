from __future__ import annotations

import subprocess
from typing import List


def run_system_cmd(cmd: list[str]):
    # Start the subprocess
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Read the standard output and standard error in real-time
    while True:
        if process.stdout:
            output = process.stdout.readline().decode().strip()
        elif process.stderr:
            output = process.stderr.readline().decode().strip()
        else:
            output = ""

        if output == "" and process.poll() is not None:
            break
        if output:
            print(output)

    # Wait for the subprocess to exit
    process.wait()

    # Return the exit status
    return process.returncode


def get_sysctl_value(name):
    command = ["sysctl", name]
    output = subprocess.check_output(command).decode().strip()
    value = output.split(" = ")[1]
    return value


def is_network_stack_tweaked():
    return (
        get_sysctl_value("net.ipv4.tcp_congestion_control") == "bbr"
    )


def is_service_running(service_name: str):
    cmd = ["systemctl", "is-active", "--quiet", service_name]
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False
