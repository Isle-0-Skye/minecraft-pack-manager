import subprocess
import sys

from dataclasses import dataclass
from pathlib import Path

from minecraft_pack_manager import APP_PACKAGE
from minecraft_pack_manager.gui.container import Container
from minecraft_pack_manager.gui.dialogs import InvalidSettingDialog, ValidSettingDialog
from minecraft_pack_manager.gui.page import BasePage, Page
from minecraft_pack_manager.lib.settings import APP_IMAGE_VAULT
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QPushButton


# < ----------------------------------------------------------------------- > #


@dataclass
class Setting:
    label: QLabel
    input: QLineEdit
    icon: QPushButton
    type: str
    name: str


# < ----------------------------------------------------------------------- > #


class SettingsPage(BasePage):
    def __init__(self, app: QApplication, container: Container) -> None:
        super().__init__(app, container)

        # < attributes > #
        self.app: QApplication = app
        self.container: Container = container

        # < layout - margins > #
        self.setContentsMargins(0, 0, 0, 0)

        # < layout - page size > #
        self.setFixedSize(self.container.size())

        # < layout - widgets > #
        self.page_layout = QGridLayout()
        self.page_layout.setContentsMargins(8, 0, 8, 8)
        self.setLayout(self.page_layout)

        # < layout - page title > #
        self.title = QLabel("Settings")
        self.title.setObjectName("pageTitle")
        self.title.setFixedSize(self.container.title_size)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_layout.addWidget(self.title, 0, 0, 1, 4, self.container.title_alignment)

        # < page buttons > #
        self.settings_widgets: dict[str, Setting] = {}
        self.settings: dict[str, str] = {
            "Instances Path:": "path",
            "Launcher Path:": "path",
        }

        row = 1

        # < page buttons - settings > #
        for setting in self.settings:
            # < page buttons - settings label > #
            setting_label = QLabel(setting)
            setting_label.setFixedSize(self.container.secondary_button_size)
            setting_label.setFixedWidth(
                setting_label.width() + self.container.secondary_button_size.height()
            )

            setting_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)

            self.page_layout.addWidget(setting_label, row, 0)

            # < page buttons - settings input > #
            setting_input = QLineEdit()
            setting_input.setFixedSize(448, self.container.secondary_button_size.height())

            self.page_layout.addWidget(setting_input, row, 1, 1, 3)

            # < page buttons - settings icon > #
            setting_icon = QPushButton()
            setting_icon.setObjectName("iconButton")

            setting_icon.setFixedSize(
                self.container.secondary_button_size.height(),
                self.container.secondary_button_size.height(),
            )

            setting_icon_icon = APP_IMAGE_VAULT.getImageIcon("offline")
            setting_icon.setIcon(setting_icon_icon)
            setting_icon.setIconSize(self.container.secondary_icon_size)

            setting_icon.clicked.connect(lambda: self.invalidPathSetting())
            self.page_layout.addWidget(
                setting_icon, row, 3, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight
            )

            # < page buttons - settings dataclass dict > #
            setting_name = setting.lower().replace(" ", "_").strip(":")
            self.settings_widgets[setting_name] = Setting(
                setting_label,
                setting_input,
                setting_icon,
                self.settings[setting],
                setting_name,
            )

            row = row + 1

        # < page buttons - validate all > #
        self.validate_all = QPushButton("Validate")
        self.validate_all.setFixedSize(self.container.secondary_button_size)

        self.validate_all.clicked.connect(lambda: self.validateSettings())
        self.page_layout.addWidget(self.validate_all, row, 0)

        # < page buttons - validate all > #
        self.update_app = QPushButton("Update MPM")
        self.update_app.setFixedSize(self.container.secondary_button_size)

        self.update_app.clicked.connect(lambda: self.updateApp())
        self.page_layout.addWidget(self.update_app, row, 2)

        # < page buttons - home > #
        self.home_button = QPushButton("Back")
        self.home_button.setFixedSize(self.container.secondary_button_size)

        self.home_button.clicked.connect(lambda: self.container.setPage(Page.Home))
        self.page_layout.addWidget(self.home_button, row, 3)

        self.loadSettings()
        self.validateSettings()

    # < ------------------------------------------------------------------- > #

    def updateApp(self) -> None:
        print("updating")

        if sys.platform == "linux":
            command = [
                "bash",
                "-c",
                f"sleep 3 ; {sys.executable} -m photon update github:Isle-0-Skye.minecraft-pack-manager ; {sys.executable} -m minecraft_pack_manager --gui",
            ]
            process = subprocess.Popen(
                command,
                start_new_session=True,
            )
        else:
            command = [
                sys.executable,
                "-m",
                "photon",
                "update",
                "github:Isle-0-Skye.minecraft-pack-manager",
            ]
            process = subprocess.Popen(
                command,
                start_new_session=True,
                creationflags=subprocess.DETACHED_PROCESS,
            )

        self.app.exit()

    # < ------------------------------------------------------------------- > #

    def loadSettings(self) -> None:
        config = APP_PACKAGE.getConfig().getConfig()

        for setting in config:
            self.settings_widgets[setting].input.setText(config[setting])

    # < ------------------------------------------------------------------- > #

    def invalidPathSetting(
        self,
        accept_show: bool = False,
        message: str = "Invalid Path",
        setting: Setting | None = None,
    ) -> None:
        dialog = InvalidSettingDialog(self, message, "Create Path", accept_show)
        if dialog.exec_():
            if setting is None:
                return
            Path(setting.input.text()).mkdir(parents=True, exist_ok=True)
            self.validatePathSetting(setting)

    # < ------------------------------------------------------------------- > #

    def validPathSetting(self, setting: Setting) -> None:
        dialog = ValidSettingDialog(self, "Valid Path", accept_show=False)
        dialog.exec_()

        config = APP_PACKAGE.getConfig().getConfig()
        config[setting.name] = setting.input.text()

        APP_PACKAGE.getConfig().setConfig(config)
        APP_PACKAGE.getConfig().writeConfig()

    # < ------------------------------------------------------------------- > #

    def invalidSetting(self, setting: Setting | None = None) -> None:
        print("invalid")

    # < ------------------------------------------------------------------- > #

    def validateSettings(self) -> None:
        for setting_name in self.settings_widgets:
            setting: Setting = self.settings_widgets[setting_name]
            setting_type: str = setting.type

            match setting_type:
                case "path":
                    self.validatePathSetting(setting)

                case _:
                    print(f"unknown setting_type: {setting_type}")

    # < ------------------------------------------------------------------- > #

    def validatePathSetting(self, setting: Setting) -> None:
        path = Path(setting.input.text())

        setting.icon.clicked.disconnect()

        try:
            path.exists()
        except PermissionError:
            message = "Permission Error"
            setting.icon.clicked.connect(lambda: self.invalidPathSetting(False, message))
            return

        if path.exists() and path.parts.__len__() > 3:
            setting.icon.clicked.connect(lambda: self.validPathSetting(setting))
            icon = APP_IMAGE_VAULT.getImageIcon("online")

        elif path.parts.__len__() > 3:
            message = "Path does not exist"
            setting.icon.clicked.connect(lambda: self.invalidPathSetting(True, message, setting))
            icon = APP_IMAGE_VAULT.getImageIcon("offline")

        else:
            message = "Path too short or missing"
            setting.icon.clicked.connect(lambda: self.invalidPathSetting(False, message))
            icon = APP_IMAGE_VAULT.getImageIcon("offline")

        setting.icon.setIcon(icon)

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
