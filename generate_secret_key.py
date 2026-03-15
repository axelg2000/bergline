"""Generate a Django SECRET_KEY and write it to .env.

Run once when setting up a new environment:
    python generate_secret_key.py
"""

import secrets
from pathlib import Path


def main():
    env_path = Path(__file__).resolve().parent / ".env"

    # Check if SECRET_KEY already exists
    if env_path.exists():
        lines = env_path.read_text().splitlines()
        for line in lines:
            if line.strip().startswith("SECRET_KEY=") and line.split("=", 1)[1].strip():
                print("SECRET_KEY already set in .env — no changes made.")
                return
    else:
        lines = []

    # token_urlsafe produces only alphanumeric, hyphens, and underscores.
    # No #, $, %, or quotes that could break .env parsers.
    key = secrets.token_urlsafe(50)

    lines.append(f"SECRET_KEY={key}")
    env_path.write_text("\n".join(lines) + "\n")
    print(f"SECRET_KEY written to {env_path}")


if __name__ == "__main__":
    main()
