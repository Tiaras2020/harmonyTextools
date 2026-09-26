"""Release settings shared by Windows and WSL delivery helpers."""
import json
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def release():
    data = json.loads((ROOT / "texstudio-harmony/release.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"\d+\.\d+\.\d+", data["version"]):
        raise ValueError("Invalid release version")
    override = os.environ.get("PACKAGE_VERSION")
    if override and override != data["version"]:
        raise ValueError("PACKAGE_VERSION disagrees with release.json; edit the single release configuration")
    return data


if __name__ == "__main__":
    print(release()["version"])
