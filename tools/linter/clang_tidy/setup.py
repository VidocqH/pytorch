import subprocess
import sys
import os
from typing import List


def run_cmd(cmd: List[str]):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    stdout, stderr = result.stdout.decode("utf-8"), result.stderr.decode("utf-8")
    print(stdout, stderr)
    if not result.returncode:
        print(f"Failed to run {cmd}")
        exit(1)


def run_timed_cmd(cmd: List[str]):
    run_cmd(["time"] + cmd)


def update_submodules():
    run_cmd(["git", "submodule", "update", "--init", "--recursive"])


def gen_compile_commands():
    os.environ["USE_NCCL"] = "0"
    os.environ["USE_DEPLOY"] = "1"
    run_timed_cmd([sys.executable, "setup.py", "--cmake-only", "build"])


def run_autogen():
    run_timed_cmd(
        [
            sys.executable,
            "-m",
            "tools.codegen.gen",
            "-s",
            "aten/src/ATen",
            "-d",
            "build/aten/src/ATen",
        ]
    )

    run_timed_cmd(
        [
            sys.executable,
            "tools/setup_helpers/generate_code.py",
            "--declarations-path",
            "build/aten/src/ATen/Declarations.yaml",
            "--native-functions-path",
            "aten/src/ATen/native/native_functions.yaml",
            "--nn-path",
            "aten/src",
        ]
    )


def setup():
    update_submodules()
    gen_compile_commands()
    run_autogen()
