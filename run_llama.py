from __future__ import annotations

import subprocess
import sys
from pathlib import Path


MODEL_DIR = Path(
    "/home/e/Qwen2.5-Coder-1.5B-Instruct-GGUF"
)

MODEL = (
    MODEL_DIR
    / "qwen2.5-coder-1.5b-instruct-q2_k.gguf"
)

SERVER = (
    MODEL_DIR
    / "llama.cpp"
    / "llama-b10295"
    / "llama-server"
)

HOST = "127.0.0.1"
PORT = "8001"
CONTEXT_SIZE = "2048"


def main() -> None:

    if not MODEL.exists():
        raise SystemExit(
            f"Model not found: {MODEL}"
        )

    if not SERVER.exists():
        raise SystemExit(
            f"llama-server not found: {SERVER}"
        )

    command = [
        str(SERVER),

        "-m",
        str(MODEL),

        "--host",
        HOST,

        "--port",
        PORT,

        # Context window for the local coding model.
        "-c",
        CONTEXT_SIZE,

        # ONE CPU THREAD.
        "-t",
        "1",

        # Small batch to keep CPU/RAM pressure low.
        "-b",
        "256",

        # One parallel sequence.
        "-np",
        "1",
    ]

    print("========================================")
    print(" CodeAgent Local LLM Server")
    print("========================================")
    print(f"Model : {MODEL.name}")
    print("Backend: CPU")
    print("Threads: 1")
    print(f"API    : http://{HOST}:{PORT}")
    print("========================================")
    print()

    try:
        subprocess.run(
            command,
            check=True,
        )

    except KeyboardInterrupt:
        print("\nServer stopped.")

    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"llama-server exited with code {exc.returncode}"
        )


if __name__ == "__main__":
    main()
