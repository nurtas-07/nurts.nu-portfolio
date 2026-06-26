import os
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_ENV_PATH = Path(__file__).resolve().parent / ".env"


def parse_sys_args(argv=None):
    argv = list(argv) if argv is not None else []
    result = {
        "debug": False,
        "mode": "polling",
        "env_file": str(DEFAULT_ENV_PATH),
        "token": None,
        # AI removed — no gemini key required
    }
    for raw_item in argv:
        if raw_item == "--debug":
            result["debug"] = True
            continue
        if raw_item.startswith("--mode="):
            result["mode"] = raw_item.split("=", 1)[1].strip() or result["mode"]
            continue
        if raw_item.startswith("--env-file="):
            result["env_file"] = raw_item.split("=", 1)[1].strip() or result["env_file"]
            continue
        if raw_item.startswith("--token="):
            result["token"] = raw_item.split("=", 1)[1].strip()
            continue
        # --gemini-key removed
    return result


def load_config(argv=None):
    args = parse_sys_args(argv)
    load_dotenv(dotenv_path=args["env_file"], override=False)

    bot_token = args["token"] or os.getenv("BOT_TOKEN", "").strip()

    return {
        "BOT_TOKEN": bot_token,
        "DEBUG": args["debug"],
        "MODE": args["mode"],
    }
