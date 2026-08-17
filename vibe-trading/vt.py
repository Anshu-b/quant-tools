#!/usr/bin/env python3

import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESEARCH_DIR = BASE_DIR / "research"
EXPERIMENTS_DIR = RESEARCH_DIR / "experiments"
JOURNAL_PATH = RESEARCH_DIR / "journal.md"


def ensure_directories():
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    if not JOURNAL_PATH.exists():
        JOURNAL_PATH.write_text(
            "# Quant Research Journal\n\n"
            "Experiments run through Vibe-Trading.\n\n"
            "---\n\n",
            encoding="utf-8",
        )


def slugify(text: str, max_length: int = 60) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:max_length].rstrip("-") or "experiment"


def build_experiment_filename(prompt: str, timestamp: datetime) -> str:
    date_part = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    slug = slugify(prompt)
    return f"{date_part}_{slug}.md"


def format_entry(
    prompt: str,
    output: str,
    formatted_time: str,
) -> str:
    return (
        f"## {formatted_time}\n\n"
        f"### Prompt\n\n"
        f"{prompt.strip()}\n\n"
        f"### Vibe-Trading Response\n\n"
        f"{output if output else '_No output captured._'}\n\n"
        f"### My Notes\n\n"
        f"- \n\n"
        f"---\n\n"
    )


def format_experiment_file(
    prompt: str,
    output: str,
    formatted_time: str,
) -> str:
    return (
        f"# Quant Experiment\n\n"
        f"**Date:** {formatted_time}\n\n"
        f"## Prompt\n\n"
        f"{prompt.strip()}\n\n"
        f"## Vibe-Trading Response\n\n"
        f"{output if output else '_No output captured._'}\n\n"
        f"## My Notes\n\n"
        f"- \n"
    )


def run_vibe_trading(prompt: str) -> int:
    ensure_directories()

    timestamp = datetime.now().astimezone()
    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")

    vibe_executable = shutil.which("vibe-trading")

    if vibe_executable is None:
        print(
            "Error: 'vibe-trading' was not found in the current environment.\n"
            "Activate your Vibe-Trading virtual environment first."
        )
        return 1

    command = [
        vibe_executable,
        "run",
        "-p",
        prompt,
    ]

    print("\nRunning Vibe-Trading...\n")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    output_lines = []

    assert process.stdout is not None

    for line in process.stdout:
        print(line, end="")
        output_lines.append(line)

    return_code = process.wait()
    output = "".join(output_lines).strip()

    # Append to master journal
    entry = format_entry(
        prompt=prompt,
        output=output,
        formatted_time=formatted_time,
    )

    with JOURNAL_PATH.open("a", encoding="utf-8") as journal:
        journal.write(entry)

    # Create standalone experiment file
    experiment_filename = build_experiment_filename(prompt, timestamp)
    experiment_path = EXPERIMENTS_DIR / experiment_filename

    experiment_path.write_text(
        format_experiment_file(
            prompt=prompt,
            output=output,
            formatted_time=formatted_time,
        ),
        encoding="utf-8",
    )

    print(f"\n\nSaved to master journal:")
    print(f"  {JOURNAL_PATH}")

    print(f"\nSaved standalone experiment:")
    print(f"  {experiment_path}")

    return return_code


def main():
    if len(sys.argv) < 2:
        print('Usage: vt "your research prompt"')
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    sys.exit(run_vibe_trading(prompt))


if __name__ == "__main__":
    main()