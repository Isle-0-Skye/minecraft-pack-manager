import json
import subprocess

from dataclasses import dataclass
from pathlib import Path

from minecraft_pack_manager import APP_PACKAGE, APP_PATHS
from PySide6.QtWidgets import QComboBox


# < ----------------------------------------------------------------------- > #


@dataclass
class RemoteInfo:
    remote: str
    upstreams: list[str]
    paths: list[str]
    names: list[str]


# < ----------------------------------------------------------------------- > #


def updateListFromLocal(to_update: QComboBox) -> None:
    config = APP_PACKAGE.getConfig().getConfig()
    path = config.get("instances_path")

    if path is None:
        return

    for entry in Path(path).iterdir():
        if not entry.is_dir():
            continue

        to_update.addItem(f"LOCL:{entry.name}")


# < ------------------------------------------------------------------- > #


def updateListFromRemote(to_update: QComboBox) -> None:
    if Path("/etc/os-release").exists() or Path("/usr/lib/os-release").exists():
        rclone_exe = APP_PATHS.root().joinpath("third_party", "rclone", "rclone")
    else:
        rclone_exe = APP_PATHS.root().joinpath("third_party", "rclone", "rclone.exe")

    if not rclone_exe.exists():
        return None

    rclone_config_file = APP_PATHS.settings().joinpath("rclone.conf")

    if not rclone_config_file.exists():
        return None

    lines: list[str] = []
    with open(rclone_config_file) as rclone_config:
        lines = rclone_config.readlines()

    remotes: list[RemoteInfo] = []
    i = 1
    for line in lines:
        if line == "type = combine\n":
            combine = lines[i - 2].strip("\n")
            if not combine.startswith("[") or not combine.endswith("]"):
                continue
            combine = combine.removeprefix("[").removesuffix("]")

            upstreams = lines[i].strip("\n")
            if not upstreams.startswith("upstreams = ") or not upstreams.endswith(":"):
                continue
            upstreams = upstreams.removeprefix("upstreams = ").strip()

            j = 0
            upstreams_list = upstreams.split(":")
            for upstream in upstreams_list:
                upstream = upstream.strip()
                upstream = upstream.split("=")[0]
                upstreams_list[j] = upstream.strip()
                j = j + 1
            upstreams_list.pop()

            remotes.append(RemoteInfo(combine, upstreams_list, [], []))

        i = i + 1

    rclone_args = [
        rclone_exe.as_posix(),
        "lsjson",
        "drive",
        "--max-depth=3",
        f"--config={rclone_config_file}",
        "--transfers=8",
        "--checkers=8",
        "--max-backlog=-1",
        "--cutoff-mode=soft",
        "--buffer-size=16M",
        "--dirs-only",
        "--no-modtime",
        "--no-mimetype",
    ]

    for remote in remotes:
        rclone_args[2] = f"{remote.remote}:"

        response = subprocess.run(rclone_args, capture_output=True, text=True)

        if response.returncode != 0:
            continue

        entries: list[dict[str, str | int | bool]] = json.loads(response.stdout)

        for entry in entries:
            path = entry.get("Path")

            if type(path) is not str:
                continue

            if "/Modpacks/" not in path:
                continue

            remote.paths.append(path)
            remote.names.append(":".join(path.split("/Modpacks/")))

    for remote in remotes:
        to_update.addItems(remote.names)


# < ------------------------------------------------------------------- > #


def transfer(source_input: QComboBox, destination_input: QComboBox) -> None:
    if Path("/etc/os-release").exists() or Path("/usr/lib/os-release").exists():
        rclone_exe = APP_PATHS.root().joinpath("third_party", "rclone", "rclone")
    else:
        rclone_exe = APP_PATHS.root().joinpath("third_party", "rclone", "rclone.exe")

    if not rclone_exe.exists():
        return None

    rclone_config_file = APP_PATHS.settings().joinpath("rclone.conf")

    if not rclone_config_file.exists():
        return None

    rclone_args = [
        f"{rclone_exe.as_posix()}",
        "sync",
        "source",
        "destination",
        f"--config={rclone_config_file}",
        "--transfers=16",
        "--checkers=24",
        "--fast-list",
        "--max-backlog=-1",
        "--cutoff-mode=soft",
        "--stats=1s",
        "--progress",
        "--progress-terminal-title",
        "--server-side-across-configs",
        "--buffer-size=16M",
        "--exclude={logs/**, backups/**, screenshots/**, options.txt}",
        # "--dry-run",
    ]

    config = APP_PACKAGE.getConfig().getConfig()
    path = config.get("instances_path")

    if path is None:
        return

    rclone_args[2] = source_input.currentText().replace("LOCL:", f"{path}/")
    rclone_args[3] = destination_input.currentText().replace("LOCL:", f"{path}/")

    if rclone_args[2].__len__() < 5 or rclone_args[3].__len__() < 5:
        return

    lines: list[str] = []
    with open(rclone_config_file) as rclone_config:
        lines = rclone_config.readlines()

    remotes: list[RemoteInfo] = []
    i = 1
    for line in lines:
        if line == "type = combine\n":
            combine = lines[i - 2].strip("\n")
            if not combine.startswith("[") or not combine.endswith("]"):
                continue
            combine = combine.removeprefix("[").removesuffix("]")

            upstreams = lines[i].strip("\n")
            if not upstreams.startswith("upstreams = ") or not upstreams.endswith(":"):
                continue
            upstreams = upstreams.removeprefix("upstreams = ").strip()

            j = 0
            upstreams_list = upstreams.split(":")
            for upstream in upstreams_list:
                upstream = upstream.strip()
                upstream = upstream.split("=")[0]
                upstreams_list[j] = upstream.strip()
                j = j + 1
            upstreams_list.pop()

            remotes.append(RemoteInfo(combine, upstreams_list, [], []))

        i = i + 1

    if destination_input.currentText() == "Make New Folder":
        destination, name = source_input.currentText().split(":")

        if destination != "LOCL":
            destination = "LOCL"
            rclone_args[3] = Path(path).joinpath(name).as_posix()

        else:
            destination = "HTZ0"

    else:
        destination, name = destination_input.currentText().split(":")

    for remote in remotes:
        if destination == "LOCL":
            destination, name = source_input.currentText().split(":")
            if destination == "HTZ0":
                remote.remote = "HTZ"
            rclone_args[2] = f"{remote.remote}:{destination}/Modpacks/{name}"
            break

        if destination in remote.upstreams:
            rclone_args[3] = f"{remote.remote}:{destination}/Modpacks/{name}"
            break

    if rclone_args[3] == "destination" or rclone_args[3] == "Make New Folder":
        return

    # if Path("/etc/os-release").exists() or Path("/usr/lib/os-release").exists():
    # args = ["gnome-terminal", "-e", f"bash -c '{" ".join(rclone_args)} ; exec bash'"]
    # else:
    # args = rclone_args

    for arg in rclone_args:
        print(arg)

    rc = subprocess.run(rclone_args)
    print(f"finished with exit code: {rc.returncode}")


# < ------------------------------------------------------------------- > #
