#< ------------------------ >#
def print_import_error(
        import_tree:str, 
        error:Exception, 
        link:str=None, # type: ignore
        text:str=None, # type: ignore
        import_type:str="Installed",
        hypertext:bool=True
    ):
    print(f"{import_type} Import Error: {import_tree}",
          f"  {error.args[0].split("(")[0]}", sep=os.linesep)
    if hypertext:
        hyperlink=f"\x1b]8;{""};{link}\x1b\\{text}\x1b]8;;\x1b\\"
        print(f"  Is {hyperlink} installed?")
    sys.exit(1)
#< ------------------------ >#

#< pre-installed imports >#
from base64 import b64decode
from typing import Any
import json
import os
import shutil
import subprocess
import sys
#< ------------------------ >#

#< not pre installed imports >#
try:
    from PIL import (
        Image
    )
except Exception as error:
    print_import_error("[logic]<-[PIL]", error,
        "https://pypi.org/project/pillow", "pillow")

try:
    from PyQt6.QtCore import (
        QDir,
        QSize
    )
except Exception as error:
    print_import_error("[logic]<-[PyQt6.QtCore]", error,
        "https://pypi.org/project/PyQt6", "PyQt6")

try:
    from PyQt6.QtGui import (
        QIcon, 
        QPixmap
    )
except Exception as error:
    print_import_error("[logic]<-[PyQt6.QtGui]", error,
        "https://pypi.org/project/PyQt6", "PyQt6")

try:
    from PyQt6.QtWidgets import (
        QPushButton
    )
except Exception as error:
    print_import_error("[logic]<-[PyQt6.QtWidgets]", error,
        "https://pypi.org/project/PyQt6", "PyQt6")

try:
    from send2trash import (
        send2trash
    )
except Exception as error:
    print_import_error("[logic]<-[send2trash]", error, 
        "https://pypi.org/project/send2trash", "send2trash")

try:
    import requests
except Exception as error:
    print_import_error("[logic]<-[requests]", error, 
        "https://pypi.org/project/requests", "requests")

try:
    import yaml
except Exception as error:
    print_import_error("[logic]<-[yaml]", error, 
        "https://pypi.org/project/PyYAML", "PyYAML")
#< ------------------------ >#

#< photon provided imports >#
try:
    from ..modules.common import (
        _UNIVERSALS, 
        log,
        projectManifest
    )
except Exception as error:
    print_import_error("[logic]<-[..modules.common]", error, 
        import_type="Photon", hypertext=False)
#< ----------------------- >#



#< ------------------------ >#
manifest=projectManifest("minecraft_pack_manager")
#< ------------------------ >#



#< ------------------------ >#
class localSettings():
    def __init__(
            self
        ):

        self.image_config_filepath=os.path.join(
            _UNIVERSALS.package_root(manifest.name()), 
            "settings", "image_config.yaml")

        self.style_sheet_filepath=os.path.join(
            _UNIVERSALS.package_root(manifest.name()), 
            "settings", "style_sheet.css")

        try:
            self.style_sheet_data=open(self.style_sheet_filepath).read()
        except:
            log.warning("failed to read style sheet")
            self.style_sheet_data=""

    def image_config(
            self
        ) -> str:

        return self.image_config_filepath


    def style_sheet(
            self
        ) -> str:

        return self.style_sheet_filepath


    def style_sheet_contents(
            self
        ) -> str:

        return self.style_sheet_data

local_settings=localSettings()
#< ------------------------ >#



#< ------------------------ >#
def is_valid_image(
        image_filepath:str
    ) -> bool:

    try:
        with Image.open(image_filepath) as file:
            file.verify()
            return True
    except Exception:
        return False
#< ------------------------ >#



#< ------------------------ >#
class imageVault():
    def __init__(
            self
        ):

        image_config_filepath=local_settings.image_config()
        images=os.path.join(
            _UNIVERSALS.package_root(manifest.name()), 
            "resources", "images")
        fallback_icon=os.path.join(images, "failed_to_load_image.png")
        QDir.addSearchPath("images", images)

        try:
            with open(image_config_filepath) as image_config_file:
                self.image_config=yaml.safe_load(image_config_file)
        except:
            log.error("Failed to load image_config.yaml")
            self.image_config={}

        for page_header in self.image_config:
            for image in self.image_config[page_header]:
                image_filepath=os.path.join(
                    images, self.image_config[page_header][image])

                if is_valid_image(image_filepath):
                    self.image_config[page_header][image]=image_filepath
                else:
                    self.image_config[page_header][image]=fallback_icon


    def images_dict(
            self
        ) -> dict[str, Any]:

        return self.image_config

images_vault=imageVault()
#< ------------------------ >#



#< ----------------------- >#
def get_QPixmap(
        image_path:str, 
        scale:bool=True, 
        size:tuple[int, int]=(64, 64)
    ) -> QPixmap:
    """
    takes a file path in the form of a str and returns a QPixmap of the file
    """

    pixmap=QPixmap(image_path)
    if scale:
        pixmap=pixmap.scaled(size[0], size[1])
    return pixmap
#< ----------------------- >#



#< ----------------------- >#
def get_QIcon(
        image_path:str, 
        scale:bool=True, 
        size:tuple[int, int]=(64, 64)
    ) -> QIcon:
    """
    takes a file path in the form of a str and returns a QIcon of the file
    """

    pixmap=get_QPixmap(image_path, scale, size)
    return QIcon(pixmap)
#< ----------------------- >#



#< ----------------------- >#
def read_settings():
    settings_data={"format_version": 1}
    try:
        with open(os.path.join(
            _UNIVERSALS.package_root(manifest.name()), 
            "settings", "user_config.yaml"), "r") as settings_file:
            settings_data=yaml.safe_load(settings_file)
    except FileNotFoundError:
        log.warning("settings file not found")
    except:
        log.error("Failed to read user settings")

    if settings_data == None:
        settings_data={"format_version": 1}

    return settings_data
#< ----------------------- >#



#< ----------------------- >#
def write_settings(settings_data):
    with open(os.path.join(
        _UNIVERSALS.package_root(manifest.name()), 
        "settings", "user_config.yaml"), "w") as settings_file:
        yaml.safe_dump(settings_data, settings_file)
#< ----------------------- >#



#< ----------------------- >#
def validate_path_setting(self, path, icons, setting_name, icon_widget, write):
    if os.path.exists(path):
        log.info(f"[{setting_name}] file path exists")

        if path.endswith(os.sep):
            path=path[-1]
        split_path=path.split(os.sep)

        if len(split_path) < 3:
            log.warning(f"[{setting_name}] file path too short")
            icons[icon_widget].setIcon(get_QIcon(
                images_vault.images_dict()["settings_page"]["invalid"]))
            icons[icon_widget].clicked.disconnect()
            icons[icon_widget].clicked.connect(lambda: [
                self.settings_popup("The provdied path is not valid: \n too short")])

        else:
            icons[icon_widget].setIcon(get_QIcon(
                images_vault.images_dict()["settings_page"]["valid"]))

            settings_data=read_settings()
            try:
                settings_data[setting_name]=path
            except Exception as error:
                log.error(error)

            if write:
                write_settings(settings_data)

            icons[icon_widget].clicked.disconnect()
            icons[icon_widget].clicked.connect(lambda: [
                self.settings_popup(f"{setting_name} is valid")])

    else:
        log.warning(f"[{setting_name}] file path does not exist")
        icons[icon_widget].setIcon(get_QIcon(
            images_vault.images_dict()["settings_page"]["invalid"]))
        icons[icon_widget].clicked.disconnect()
        icons[icon_widget].clicked.connect(lambda: [
            self.settings_popup("The provided path is not valid: \n does not exist \nWould you like to make it?", second_button=True, path=path)])
#< ----------------------- >#



#< ----------------------- >#
def validate_settings(self, widgets, icons, write=False):
    log.trace("validating all settings")
    settings={}
    for widget in widgets:
        try:
            settings[widget]=widgets[widget].text()
        except:
            log.error("Failed to read settings widget value")

    for setting in settings:
        path=settings[setting]
        match setting:
            case "launcher_path_input":
                validate_path_setting(self, path, icons, 
                    "launcher_path", "launcher_path_validate", write)

            case "instances_path_input":
                validate_path_setting(self, path, icons, 
                    "instances_path", "instances_path_validate", write)
#< ----------------------- >#



#< ----------------------- >#
def write_settings_to_gui(widgets):
    settings_data=read_settings()

    for widget in widgets:
        match widget:
            case "launcher_path_input":
                try:
                    widgets[widget].setText(settings_data["launcher_path"])
                except KeyError:
                    log.warning(f"No value set for {widget}")
                except Exception as error:
                    log.error(f"Failed to write settings widget value {error}")

            case "instances_path_input":
                try:
                    widgets[widget].setText(settings_data["instances_path"])
                except KeyError:
                    log.warning(f"No value set for {widget}")
                except Exception as error:
                    log.error(f"Failed to write settings widget value {error}")
#< ----------------------- >#



#< ----------------------- >#
def read_player_data() -> dict[Any, Any]:
    player_data={"format_version": 1}
    try:
        with open(os.path.join(
            _UNIVERSALS.package_root(manifest.name()), 
            "settings", "players.yaml"), "r") as settings_file:
            player_data=yaml.safe_load(settings_file)
    except FileNotFoundError:
        log.warning("players file not found")
    except:
        log.error("Failed to read players file")

    if player_data == None:
        player_data={"format_version": 1}

    return player_data
#< ----------------------- >#



#< ----------------------- >#
def write_player_data(player_data):
    try:
        format_version=player_data.pop("format_version")
    except:
        format_version='"format_version": 1\n'
    else:
        format_version=f'"format_version": {format_version}\n'

    # player_data=format_version.update(player_data)

    with open(os.path.join(
        _UNIVERSALS.package_root(manifest.name()), 
        "settings", "players.yaml"), "w") as settings_file:
        settings_file.write(format_version)
        yaml.safe_dump(player_data, settings_file)
#< ----------------------- >#



#< ----------------------- >#
def user_list():
    usernames=[]
    player_data=read_player_data()
    for i in player_data:
        if i == "format_version":
            continue

        username=player_data[i]["username"]
        usernames.append(username)

    return usernames
#< ----------------------- >#



#< ----------------------- >#
def reload_player_labels(self):
    log.info("reloading player labels")
    player_data=read_player_data()

    for id in player_data:
        if id == "format_version":
            continue

        username=player_data[id]["username"]
        user_face=os.path.join(
            _UNIVERSALS.package_root(manifest.name()), 
            "resources", "skins", f"{username}_face.png")
        user_skin=os.path.join(
            _UNIVERSALS.package_root(manifest.name()), 
            "resources", "skins", f"{username}_skin.png")

        if not os.path.exists(user_face):
            if os.path.exists(user_skin):
                try:
                    skin=Image.open(user_skin)
                except:
                    log.warning("Failed to open player skin png")
                else:
                    face=skin.crop((8, 8, 16, 16))
                    face.save(user_face)

            else:
                user_face=images_vault.images_dict()["play_page"]["unknown_icon"]

        try:
            label:QPushButton=self.user_labels[username]
            log.debug(f"Using existing label for Index: {id}, User: {username}")

        except:
            log.debug(f"Creating label for Index: {id}, User: {username}")

            self.user_label=QPushButton(text=username)
            self.user_label.setObjectName("user_label_left")
            self.user_label.setFixedSize(320, 64)
            self.user_label.setIcon(get_QIcon(user_face))
            self.user_label.setIconSize(QSize(48, 48))

            self.active_icon=QPushButton()
            self.active_icon.setObjectName("user_label_right")
            self.active_icon.setFixedSize(64, 64)
            self.active_icon.setIcon(get_QIcon(
                images_vault.images_dict()["play_page"]["offline_icon"]))
            self.active_icon.setIconSize(QSize(32, 32))

            self.user_labels[username]=self.user_label
            self.user_active_icons[username]=self.active_icon
            self.user_list.addRow(self.user_label, self.active_icon)

        else:
            log.info(f"Updating Icon for Index: {id}, User: {username}")
            label.setIcon(get_QIcon(user_face, size=(48, 48)))
            label.setIconSize(QSize(48, 48))

    usernames=[]
    for id in player_data:
        if id != "format_version":
            usernames.append(player_data[id]["username"])

    remove=False
    for name in self.user_labels:
        if name not in usernames:
            self.user_list.removeRow(self.user_labels[name])
            remove=True
            break

    if remove:
        self.user_labels.pop(name)
        delete_player_skin(name)
#< ----------------------- >#



#< ----------------------- >#
def edit_users(self):
    player_data=read_player_data()

    if self.tabs.currentIndex():
        selected_username=self.remove_user_tab.username_input.currentText()

        data={"format_version": 1}
        for i in player_data:
            if i == "format_version":
                continue

            if player_data[i]["username"] != selected_username:
                data[i]=player_data[i]
        write_player_data(data)

    else:
        selected_username=self.add_user_tab.username_input.text()
        selected_auth_type=self.add_user_tab.auth_type_input.currentText()

        usernames=[]
        used_ids=[]
        for i in player_data:
            if i == "format_version":
                continue

            usernames.append(player_data[i]["username"])
            used_ids.append(i)
        used_ids=sorted(used_ids)

        x=0
        for i in used_ids:
            x=x+1
            if i != x:
                x=x-1
                break

        if selected_username not in usernames:
            player_data[x+1]={
                "username": selected_username, 
                "auth": selected_auth_type}

        write_player_data(player_data)
#< ----------------------- >#



#< ------------------------ >#
def get_player_skin():
    player_data=read_player_data()

    for id in player_data:
        if id == "format_version":
            continue

        try:
            auth=player_data[id]["auth"]
        except:
            auth="Official"

        username=player_data[id]["username"]
        user_skin=os.path.join(
            _UNIVERSALS.package_root(manifest.name()), 
            "resources", "skins", f"{username}_skin.png")

        match auth:
            case "Ely":
                log.debug(f"fetching http://skinsystem.ely.by/skins/{username}.png")
                response=requests.get(f"http://skinsystem.ely.by/skins/{username}.png")

                if response.status_code != 200:
                    log.warning(f"invalid response {response.status_code}")
                    continue

                with open(user_skin, "wb") as file:
                    file.write(response.content)

            case "Official":
                log.debug(f"fetching https://api.mojang.com/users/profiles/minecraft/{username}")
                response=requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")

                if response.status_code != 200:
                    log.warning(f"invalid response: {response.status_code} for username: {username}")
                    continue

                id=response.json()["id"]
                response=requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{id}")

                if response.status_code != 200:
                    log.warning(f"invalid response: {response.status_code} for id: {id}")
                    continue

                endcoded_value=response.json()["properties"][0]["value"]
                decoded_json=json.loads(b64decode(endcoded_value, validate=True).decode("utf-8"))
                skin_url = decoded_json["textures"]["SKIN"]["url"]
                response=requests.get(skin_url, stream=True)

                if response.status_code != 200:
                    log.warning(f"invalid response: {response.status_code} for skin: {skin_url}")
                    continue

                with open(user_skin, "wb") as file:
                    shutil.copyfileobj(response.raw, file)

            case _:
                log.warning(f"Invalid Auth Type {auth}")
#< ------------------------ >#



#< ------------------------ >#
def open_launcher():
    with open(os.path.join(
        _UNIVERSALS.package_root(manifest.name()), 
        "settings", "user_config.yaml"), "r") as config_file:
        config_data=yaml.safe_load(config_file)

    try:
        subprocess.Popen(config_data["launcher_path"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            stdin=subprocess.PIPE, start_new_session=True)
    except Exception as error:
        log.error(error)
#< ------------------------ >#



#< ------------------------ >#
def delete_player_skin(username):
    user_face=os.path.join(
        _UNIVERSALS.package_root(manifest.name()), 
        "resources", "skins", f"{username}_face.png")
    user_skin=os.path.join(
        _UNIVERSALS.package_root(manifest.name()), 
        "resources", "skins", f"{username}_skin.png")

    try:
        send2trash([user_face, user_skin])
    except:
        log.warning("Failed to send skin png to bin")
#< ------------------------ >#


