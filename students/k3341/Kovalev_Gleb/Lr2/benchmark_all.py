import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_script(script: str, *args: str) -> None:
    print(f"\n===== {script} =====", flush=True)
    subprocess.run([sys.executable, str(BASE_DIR / script), *args], check=True)


def main() -> None:
    run_script("task1_threading_sum.py")
    run_script("task1_multiprocessing_sum.py")
    run_script("task1_async_sum.py")
    run_script("task2_threading_parser.py", "--local")
    run_script("task2_multiprocessing_parser.py", "--local")
    run_script("task2_async_parser.py", "--local")


if __name__ == "__main__":
    main()
