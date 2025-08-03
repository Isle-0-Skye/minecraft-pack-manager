def print_import_error(
    import_tree: str,
    error: ImportError,
    hypertext: bool = True,
    import_type: str = "installed",
    link: str | None = None,
    text: str | None = None,
):
    print(
        f"{import_type} import error: {import_tree}",
        f"  {error.args[0].split('(')[0]}",
        sep=os.linesep,
    )
    if hypertext:
        hyperlink = f"\x1b]8;{''};{link}\x1b\\{text}\x1b]8;;\x1b\\"
        print(f"  is {hyperlink} installed?")
    sys.exit(1)


# < pre-installed imports --------------------------------------------------------------------- > #
import json
import os
import platform
import shutil
import subprocess
import sys

from base64 import b64decode
from pathlib import Path
from typing import Any


# < not pre installed imports ----------------------------------------------------------------- > #
try:
    from PIL import Image
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[PIL]",
        error=error,
        link="https://pypi.org/project/pillow",
        text="pillow",
    )

try:
    from PyQt6.QtCore import (
        QDir,
        QSize,
    )
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[PyQt6.QtCore]",
        error=error,
        link="https://pypi.org/project/PyQt6",
        text="PyQt6",
    )

try:
    from PyQt6.QtGui import (
        QIcon,
        QPixmap,
    )
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[PyQt6.QtGui]",
        error=error,
        link="https://pypi.org/project/PyQt6",
        text="PyQt6",
    )

try:
    from PyQt6.QtWidgets import (
        QPushButton,
    )
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[PyQt6.QtWidgets]",
        error=error,
        link="https://pypi.org/project/PyQt6",
        text="PyQt6",
    )

try:
    from send2trash import (
        send2trash,
    )
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[send2trash]",
        error=error,
        link="https://pypi.org/project/send2trash",
        text="send2trash",
    )

try:
    import requests
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[requests]",
        error=error,
        link="https://pypi.org/project/requests",
        text="requests",
    )

try:
    import yaml
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[yaml]",
        error=error,
        link="https://pypi.org/project/PyYAML",
        text="PyYAML",
    )

# < photon provided imports ------------------------------------------------------------------- > #
try:
    from ..modules.common import (
        UNIVERSALS,
        pLOG,
        text_to_hypertext,
    )
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[..modules.common]",
        error=error,
        import_type="photon",
        hypertext=False,
    )

try:
    from ..modules.manifests import (
        argumentManifest,
        projectManifest,
        sourceManifest,
    )
except ImportError as error:
    print_import_error(
        import_tree="[logic]<-[..modules.common]",
        error=error,
        import_type="photon",
        hypertext=False,
    )

# < load manifests ---------------------------------------------------------------------------- > #
hyperlink = text_to_hypertext(" ", "Minecraft Pack Manager")
try:
    PROJECT_MANIFEST = projectManifest("minecraft_pack_manager")
except FileNotFoundError:
    pLOG.warning(f"no project manifest found for: {hyperlink}")
    sys.exit(1)
except TypeError as error:
    pLOG.warning(f"invalid project manifest found for: {hyperlink} \n  {error}")
    sys.exit(1)

hyperlink = text_to_hypertext(" ", PROJECT_MANIFEST.display_name())
try:
    SOURCE_MANIFEST = sourceManifest("minecraft_pack_manager")
except FileNotFoundError:
    pLOG.warning(f"no source manifest found for: {hyperlink}")
    sys.exit(1)
except TypeError as error:
    pLOG.warning(f"invalid source manifest found for: {hyperlink} \n  {error}")
    sys.exit(1)

hyperlink = text_to_hypertext(
    SOURCE_MANIFEST.home_page(default_value=" "), PROJECT_MANIFEST.display_name()
)
try:
    ARGUMENT_MANIFEST = argumentManifest("minecraft_pack_manager")
except FileNotFoundError:
    pLOG.warning(f"no argument manifest found for: {hyperlink}")
    sys.exit(1)
except TypeError as error:
    pLOG.warning(f"invalid argument manifest found for: {hyperlink} \n  {error}")
    sys.exit(1)


# < ------------------------------------------------------------------------------------------- > #
class localSettings:
    def __init__(self) -> None:
        self.image_config_filepath = Path(
            UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "settings", "image_config.yaml"
        )

        self.style_sheet_filepath = Path(
            UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "settings", "style_sheet.css"
        )

        if self.image_config_filepath.exists():
            with open(self.image_config_filepath, "r") as image_config_data_file:
                self.image_config_file_data = yaml.safe_load(image_config_data_file)
        else:
            pLOG.warning("failed to find image config")
            self.image_config_file_data = {}

        if self.style_sheet_filepath.exists():
            self.style_sheet_file_data = open(self.style_sheet_filepath).read()
        else:
            pLOG.warning("failed to find style sheet")
            self.style_sheet_file_data = ""

    def image_config(self) -> Path:
        return self.image_config_filepath

    def image_config_data(self) -> dict[str, Any]:
        return self.image_config_file_data

    def style_sheet(self) -> Path:
        return self.style_sheet_filepath

    def style_sheet_data(self) -> str:
        return self.style_sheet_file_data


LOCAL_SETTINGS = localSettings()


# < ------------------------------------------------------------------------------------------- > #
def is_valid_image(image_filepath: str | Path) -> bool:
    if type(image_filepath) is Path:
        image_filepath = image_filepath.as_uri()

    try:
        with Image.open(image_filepath) as file:
            file.verify()
            return True
    except Exception:
        return False


# < ------------------------------------------------------------------------------------------- > #
class imageVault:
    def __init__(self) -> None:
        images = Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "resources", "images")
        fallback_icon = "failed_to_load_image.png"
        QDir.addSearchPath("images", images.as_uri())
        self.image_config = LOCAL_SETTINGS.image_config_data()

        for page_header in self.image_config:
            for image in self.image_config.get(page_header, {}):
                image_filepath = Path(
                    images, self.image_config.get(page_header, {}).get(image, fallback_icon)
                )

                if is_valid_image(image_filepath):
                    self.image_config[page_header][image] = image_filepath.as_uri()
                else:
                    self.image_config[page_header][image] = Path(images, fallback_icon).as_uri()

    def images_dict(self) -> dict[str, Any]:
        return self.image_config


IMAGES_VAULT = imageVault()


# < ------------------------------------------------------------------------------------------- > #
def get_QPixmap(image_path: str, scale: bool = True, size: tuple[int, int] = (64, 64)) -> QPixmap:
    """
    takes a file path in the form of a str and returns a QPixmap of the file
    """
    image_path = image_path.removeprefix("file://")

    pLOG.debug(f"QPIXMAP: {image_path}")
    pixmap = QPixmap(image_path)
    if scale:
        pLOG.debug(f"scaling to {size}")
        pixmap = pixmap.scaled(size[0], size[1])
    return pixmap


# < ------------------------------------------------------------------------------------------- > #
def get_QIcon(image_path: str, scale: bool = True, size: tuple[int, int] = (64, 64)) -> QIcon:
    """
    takes a file path in the form of a str and returns a QIcon of the file
    """
    image_path = image_path.removeprefix("file://")

    pLOG.debug(f"QICON: {image_path}")
    pixmap = get_QPixmap(image_path, scale, size)
    return QIcon(pixmap)


# < ------------------------------------------------------------------------------------------- > #
def read_settings() -> dict[str, Any]:
    settings_data = {"format_version": 1}
    try:
        with open(
            Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "settings", "user_config.yaml"),
            "r",
        ) as settings_file:
            settings_data = yaml.safe_load(settings_file)
    except FileNotFoundError:
        pLOG.warning("settings file not found")

    if settings_data is None:
        settings_data = {"format_version": 1}

    return settings_data


# < ------------------------------------------------------------------------------------------- > #
def write_settings(settings_data) -> None:
    with open(
        Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "settings", "user_config.yaml"), "w"
    ) as settings_file:
        yaml.safe_dump(settings_data, settings_file)


# < ------------------------------------------------------------------------------------------- > #
def validate_path_setting(self, path, icons, setting_name, icon_widget, write) -> None:
    if Path(path).exists():
        pLOG.info(f"[{setting_name}] file path exists")

        if path.endswith(os.sep):
            path = path[-1]
        split_path = path.split(os.sep)

        if len(split_path) < 3:
            pLOG.warning(f"[{setting_name}] file path too short")
            icons[icon_widget].setIcon(
                get_QIcon(IMAGES_VAULT.images_dict()["settings_page"]["invalid"])
            )
            icons[icon_widget].clicked.disconnect()
            icons[icon_widget].clicked.connect(
                lambda: [self.settings_popup("The provdied path is not valid: \n too short")]
            )

        else:
            icons[icon_widget].setIcon(
                get_QIcon(IMAGES_VAULT.images_dict()["settings_page"]["valid"])
            )

            settings_data = read_settings()
            try:
                settings_data[setting_name] = path
            except Exception as error:
                pLOG.error(error)

            if write:
                write_settings(settings_data)

            icons[icon_widget].clicked.disconnect()
            icons[icon_widget].clicked.connect(
                lambda: [self.settings_popup(f"{setting_name} is valid")]
            )

    else:
        pLOG.warning(f"[{setting_name}] file path does not exist")
        icons[icon_widget].setIcon(
            get_QIcon(IMAGES_VAULT.images_dict()["settings_page"]["invalid"])
        )
        icons[icon_widget].clicked.disconnect()
        icons[icon_widget].clicked.connect(
            lambda: [
                self.settings_popup(
                    "The provided path is not valid: \n does not exist \nWould you like to make it?",
                    second_button=True,
                    path=path,
                )
            ]
        )


# < ------------------------------------------------------------------------------------------- > #
def validate_settings(self, widgets, icons, write=False) -> None:
    pLOG.debug("validating all settings")
    settings = {}
    for widget in widgets:
        try:
            settings[widget] = widgets[widget].text()
        except Exception as error:
            pLOG.error(f"Failed to read settings widget value, {error}")

    for setting in settings:
        path = settings[setting]
        match setting:
            case "launcher_path_input":
                validate_path_setting(
                    self, path, icons, "launcher_path", "launcher_path_validate", write
                )

            case "instances_path_input":
                validate_path_setting(
                    self, path, icons, "instances_path", "instances_path_validate", write
                )


# < ------------------------------------------------------------------------------------------- > #
def write_settings_to_gui(widgets) -> None:
    settings_data = read_settings()

    for widget in widgets:
        match widget:
            case "launcher_path_input":
                try:
                    widgets[widget].setText(settings_data["launcher_path"])
                except KeyError:
                    pLOG.warning(f"No value set for {widget}")
                except Exception as error:
                    pLOG.error(f"Failed to write settings widget value {error}")

            case "instances_path_input":
                try:
                    widgets[widget].setText(settings_data["instances_path"])
                except KeyError:
                    pLOG.warning(f"No value set for {widget}")
                except Exception as error:
                    pLOG.error(f"Failed to write settings widget value {error}")


# < ------------------------------------------------------------------------------------------- > #
def read_player_data() -> dict[Any, Any]:
    player_data = {"format_version": 1}
    try:
        with open(
            Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "settings", "players.yaml"), "r"
        ) as settings_file:
            player_data = yaml.safe_load(settings_file)
    except FileNotFoundError:
        pLOG.warning("players file not found")

    if player_data is None:
        player_data = {"format_version": 1}

    return player_data


# < ------------------------------------------------------------------------------------------- > #
def write_player_data(player_data) -> None:
    try:
        format_version = player_data.pop("format_version")
    except Exception as error:
        pLOG.error(error)
        format_version = '"format_version": 1\n'
    else:
        format_version = f'"format_version": {format_version}\n'

    # player_data=format_version.update(player_data)

    with open(
        Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "settings", "players.yaml"), "w"
    ) as settings_file:
        settings_file.write(format_version)
        yaml.safe_dump(player_data, settings_file)


# < ------------------------------------------------------------------------------------------- > #
def user_list() -> list[str]:
    usernames = []
    player_data = read_player_data()
    for i in player_data:
        if i == "format_version":
            continue

        username = str(player_data[i]["username"])
        usernames.append(username)

    return usernames


# < ------------------------------------------------------------------------------------------- > #
def reload_player_labels(self) -> None:
    pLOG.info("reloading player labels")
    player_data = read_player_data()

    for id in player_data:
        if id == "format_version":
            continue

        username = player_data[id]["username"]
        user_face = Path(
            UNIVERSALS.package_root(PROJECT_MANIFEST.name()),
            "resources",
            "skins",
            f"{username}_face.png",
        )
        user_skin = Path(
            UNIVERSALS.package_root(PROJECT_MANIFEST.name()),
            "resources",
            "skins",
            f"{username}_skin.png",
        )

        if not Path(user_face).exists():
            if Path(user_skin).exists():
                try:
                    skin = Image.open(user_skin)
                except Exception as error:
                    pLOG.warning(f"Failed to open player skin png, {error}")
                else:
                    face = skin.crop((8, 8, 16, 16))
                    face.save(user_face)

            else:
                user_face = IMAGES_VAULT.images_dict()["play_page"]["unknown_icon"]

        if type(user_face) is Path:
            user_face = user_face.as_uri()
        else:
            user_face = str(user_face)

        try:
            label: QPushButton = self.user_labels[username]
            pLOG.debug(f"Using existing label for Index: {id}, User: {username}")

        except Exception as error:
            pLOG.debug(f"{error}, Creating label for Index: {id}, User: {username}")

            self.user_label = QPushButton(text=username)
            self.user_label.setObjectName("user_label_left")
            self.user_label.setFixedSize(320, 64)
            self.user_label.setIcon(get_QIcon(user_face))
            self.user_label.setIconSize(QSize(48, 48))

            self.active_icon = QPushButton()
            self.active_icon.setObjectName("user_label_right")
            self.active_icon.setFixedSize(64, 64)
            self.active_icon.setIcon(
                get_QIcon(IMAGES_VAULT.images_dict()["play_page"]["offline_icon"])
            )
            self.active_icon.setIconSize(QSize(32, 32))

            self.user_labels[username] = self.user_label
            self.user_active_icons[username] = self.active_icon
            self.user_list.addRow(self.user_label, self.active_icon)

        else:
            pLOG.info(f"Updating Icon for Index: {id}, User: {username}")
            label.setIcon(get_QIcon(user_face, size=(48, 48)))
            label.setIconSize(QSize(48, 48))

    usernames = []
    for id in player_data:
        if id != "format_version":
            usernames.append(player_data[id]["username"])

    remove = False
    for name in self.user_labels:
        if name not in usernames:
            self.user_list.removeRow(self.user_labels[name])
            remove = True
            break

    if remove:
        self.user_labels.pop(name)
        delete_player_skin(name)


# < ------------------------------------------------------------------------------------------- > #
def edit_users(self) -> None:
    player_data = read_player_data()

    if self.tabs.currentIndex():
        selected_username = self.remove_user_tab.username_input.currentText()

        data = {"format_version": 1}
        for i in player_data:
            if i == "format_version":
                continue

            if player_data[i]["username"] != selected_username:
                data[i] = player_data[i]
        write_player_data(data)

    else:
        selected_username = self.add_user_tab.username_input.text()
        selected_auth_type = self.add_user_tab.auth_type_input.currentText()

        usernames = []
        used_ids = []
        for i in player_data:
            if i == "format_version":
                continue

            usernames.append(player_data[i]["username"])
            used_ids.append(i)
        used_ids = sorted(used_ids)

        x = 0
        for i in used_ids:
            x = x + 1
            if i != x:
                x = x - 1
                break

        if selected_username not in usernames:
            player_data[x + 1] = {"username": selected_username, "auth": selected_auth_type}

        write_player_data(player_data)


# < ------------------------------------------------------------------------------------------- > #
def get_player_skin() -> None:
    player_data = read_player_data()

    for id in player_data:
        if id == "format_version":
            continue

        try:
            auth = player_data[id]["auth"]
        except Exception as error:
            pLOG.error(error)
            auth = "Official"

        username = player_data[id]["username"]
        user_skin = Path(
            UNIVERSALS.package_root(PROJECT_MANIFEST.name()),
            "resources",
            "skins",
            f"{username}_skin.png",
        )

        match auth:
            case "Ely":
                pLOG.debug(f"fetching http://skinsystem.ely.by/skins/{username}.png")
                response = requests.get(f"http://skinsystem.ely.by/skins/{username}.png")

                if response.status_code != 200:
                    pLOG.warning(f"invalid response {response.status_code}")
                    continue

                with open(user_skin, "wb") as file:
                    file.write(response.content)

            case "Official":
                pLOG.debug(f"fetching https://api.mojang.com/users/profiles/minecraft/{username}")
                response = requests.get(
                    f"https://api.mojang.com/users/profiles/minecraft/{username}"
                )

                if response.status_code != 200:
                    pLOG.warning(
                        f"invalid response: {response.status_code} for username: {username}"
                    )
                    continue

                id = response.json()["id"]
                response = requests.get(
                    f"https://sessionserver.mojang.com/session/minecraft/profile/{id}"
                )

                if response.status_code != 200:
                    pLOG.warning(f"invalid response: {response.status_code} for id: {id}")
                    continue

                endcoded_value = response.json()["properties"][0]["value"]
                decoded_json = json.loads(b64decode(endcoded_value, validate=True).decode("utf-8"))
                skin_url = decoded_json["textures"]["SKIN"]["url"]
                response = requests.get(skin_url, stream=True)

                if response.status_code != 200:
                    pLOG.warning(f"invalid response: {response.status_code} for skin: {skin_url}")
                    continue

                with open(user_skin, "wb") as file:
                    shutil.copyfileobj(response.raw, file)

            case _:
                pLOG.warning(f"Invalid Auth Type {auth}")


# < ------------------------------------------------------------------------------------------- > #
def open_launcher() -> None:
    with open(
        Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "settings", "user_config.yaml"), "r"
    ) as config_file:
        config_data = yaml.safe_load(config_file)

    try:
        subprocess.Popen(
            config_data["launcher_path"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            start_new_session=True,
        )
    except Exception as error:
        pLOG.error(error)


# < ------------------------------------------------------------------------------------------- > #
def delete_player_skin(username) -> None:
    user_face = Path(
        UNIVERSALS.package_root(PROJECT_MANIFEST.name()),
        "resources",
        "skins",
        f"{username}_face.png",
    )
    user_skin = Path(
        UNIVERSALS.package_root(PROJECT_MANIFEST.name()),
        "resources",
        "skins",
        f"{username}_skin.png",
    )

    try:
        send2trash([user_face, user_skin])
    except Exception as error:
        pLOG.warning(f"Failed to send skin png to bin, {error}")


# < ------------------------------------------------------------------------------------------- > #
def refresh_transfer_options(self) -> None:
    settings_data = read_settings()
    local_instances = {}
    remote_instances = {}
    mode = str(self).split(".gui.")[1]
    mode = mode.split("Page")[0]

    rclone_cmd = [
        f"{Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), 'tools', 'rclone', 'rclone')}",
        f"--config={settings_data['rclone_config_file']}",
        "lsjson",
        f"{settings_data['rclone_root']}:",
        "--max-depth=3",
        "--dirs-only",
        "--no-mimetype",
        "--no-modtime",
    ]

    try:
        for directory in os.listdir(settings_data["instances_path"]):
            path = Path(settings_data["instances_path"], directory)
            if Path(path).is_dir():
                local_instances[directory] = path
    except FileNotFoundError as error:
        pLOG.warning(error)

    rclone_remotes = ""
    with open(settings_data["rclone_config_file"], "r") as rcc:
        for line in rcc:
            if line.strip().startswith("upstreams"):
                rclone_remotes = line

    rclone_remotes = rclone_remotes.split(":")
    rclone_remotes[0] = rclone_remotes[0].split("=", 1)[1]
    for i in range(len(rclone_remotes)):
        rclone_remotes[i] = rclone_remotes[i].strip()
    rclone_remotes = [x for x in rclone_remotes if x]

    enders = ("Modpacks", "mods")
    for remote in rclone_remotes:
        enders = enders + (remote.split("=")[0],)

    rclone_cmd_output = subprocess.run(rclone_cmd, capture_output=True, text=True)
    pLOG.debug(rclone_cmd_output.stdout)
    pLOG.debug(rclone_cmd_output.stderr)
    rclone_data = json.loads(rclone_cmd_output.stdout)
    for obj in rclone_data:
        if not obj["Path"].endswith(enders):
            remote_instances[obj["Name"]] = obj["Path"]

    match mode:
        case "Upload":
            for key, value in local_instances.items():
                self.source_combobox.addItem(key)
            self.source_combobox.setCurrentIndex(0)

            for key, value in remote_instances.items():
                self.destination_combobox.addItem(value)
            self.destination_combobox.addItem("Make New Folder")
            self.destination_combobox.setCurrentIndex(0)

        case "Download":
            for key, value in local_instances.items():
                self.destination_combobox.addItem(key)
            self.destination_combobox.setCurrentIndex(0)
            self.destination_combobox.addItem("Make New Folder")

            for key, value in remote_instances.items():
                self.source_combobox.addItem(value)
            self.source_combobox.setCurrentIndex(0)

        case _:
            pLOG.error("invalid refresh_transfer_options mode")

    pLOG.debug(json.dumps(settings_data, indent=4))
    pLOG.debug(json.dumps(local_instances, indent=4))
    pLOG.debug(json.dumps(remote_instances, indent=4))
    pLOG.debug(rclone_cmd)


# < ------------------------------------------------------------------------------------------- > #
def start_transfer(self) -> None:
    settings_data = read_settings()
    mode = str(self).split(".gui.")[1]
    mode = mode.split("Page")[0]
    src = self.source_combobox.currentText()
    dst = self.destination_combobox.currentText()
    if src in ["", None] or dst in ["", None]:
        return
    pLOG.debug(f"{src}, {dst}")

    match mode:
        case "Upload":
            if dst == "Make New Folder":
                rclone_remotes = ""
                with open(settings_data["rclone_config_file"], "r") as rcc:
                    for line in rcc:
                        if line.strip().startswith("upstreams"):
                            rclone_remotes = line

                sizes = {}
                rclone_remotes = rclone_remotes.split(":")
                rclone_remotes[0] = rclone_remotes[0].split("=", 1)[1]
                for i in range(len(rclone_remotes)):
                    rclone_remotes[i] = rclone_remotes[i].strip()
                rclone_remotes = [x for x in rclone_remotes if x]
                for remote in rclone_remotes:
                    remote = remote.split("=")[0]

                    rclone_check_cmd = [
                        f"{Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), 'tools', 'rclone', 'rclone')}",
                        f"--config={settings_data['rclone_config_file']}",
                        "size",
                        f"{settings_data['rclone_root']}:{remote}/",
                        "--json",
                    ]
                    check_cmd = subprocess.run(rclone_check_cmd, capture_output=True, text=True)
                    pLOG.debug(check_cmd.stdout.strip())
                    pLOG.debug(check_cmd.stderr.strip())
                    data = json.loads(check_cmd.stdout.strip())
                    sizes[remote] = data["bytes"]
                dst = f"{min(sizes, key=sizes.get)}/Modpacks/"

            src = Path(settings_data["instances_path"], src)
            dst = f"{settings_data['rclone_root']}:{dst}"

        case "Download":
            if dst == "Make New Folder":
                dst = src.rsplit("/", 1)[1]

            src = f"{settings_data['rclone_root']}:{src}"
            dst = Path(settings_data["instances_path"], dst)

        case _:
            pLOG.error("invalid refresh_transfer_options mode")

    rclone_cmd = [
        f"{Path(UNIVERSALS.package_root(PROJECT_MANIFEST.name()), 'tools', 'rclone', 'rclone')}",
        f"--config={settings_data['rclone_config_file']}",
        "sync",
        f"{src}",
        f"{dst}",
    ]
    settings = (
        "--transfers=20 --checkers=50 --fast-list --max-backpLOG=10000 --drive-chunk-size=64M -P"
    )

    pLOG.info(f"source: {src}")
    pLOG.info(f"destination: {dst}")
    pLOG.info(f"full command: {rclone_cmd}")

    if platform.system() == "Windows":
        shell_cmd = []
    elif platform.system() == "Linux":
        rclone_path = Path(
            UNIVERSALS.package_root(PROJECT_MANIFEST.name()), "tools", "rclone", "rclone"
        )
        conf_path = settings_data["rclone_config_file"]
        shell_cmd = [
            "gnome-terminal",
            "-e",
            f'bash -c "{rclone_path} --config={conf_path} sync {src} {dst} -n {settings}; bash"',
        ]

    pLOG.info(shell_cmd)
    subprocess.run(shell_cmd)
