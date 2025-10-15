from minecraft_pack_manager.gui.container import Container
from minecraft_pack_manager.gui.page import BasePage, Page
from minecraft_pack_manager.lib.settings import APP_IMAGE_VAULT
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton


# < ----------------------------------------------------------------------- > #


class HomePage(BasePage):
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
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.page_layout)

        # < layout - page title > #
        self.title = QLabel("Home")
        self.title.setObjectName("pageTitle")
        self.title.setFixedSize(self.container.title_size)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_layout.addWidget(self.title, 0, 0, 1, 4, self.container.title_alignment)

        # < page buttons > #
        self.page_buttons: list[QPushButton] = []

        # < page buttons - upload > #
        self.upload_button = QPushButton("Upload")

        self.upload_button_icon = APP_IMAGE_VAULT.getImageIcon("upload")
        self.upload_button.setIcon(self.upload_button_icon)

        self.upload_button.clicked.connect(lambda: self.container.setPage(Page.Upload))
        self.page_buttons.append(self.upload_button)

        # < page buttons - download > #
        self.download_button = QPushButton("Download")

        self.download_button_icon = APP_IMAGE_VAULT.getImageIcon("download")
        self.download_button.setIcon(self.download_button_icon)

        self.download_button.clicked.connect(lambda: self.container.setPage(Page.Download))
        self.page_buttons.append(self.download_button)

        # < page buttons - play > #
        self.play_button = QPushButton("Play")

        self.play_button_icon = APP_IMAGE_VAULT.getImageIcon("mojang")
        self.play_button.setIcon(self.play_button_icon)

        self.play_button.clicked.connect(lambda: self.container.setPage(Page.Play))
        self.page_buttons.append(self.play_button)

        # < page buttons - settings > #
        self.settings_button = QPushButton("Settings")

        self.settings_button_icon = APP_IMAGE_VAULT.getImageIcon("settings")
        self.settings_button.setIcon(self.settings_button_icon)

        self.settings_button.clicked.connect(lambda: self.container.setPage(Page.Settings))
        self.page_buttons.append(self.settings_button)

        # < page buttons - help > #
        self.help_button = QPushButton("Help")

        self.help_button_icon = APP_IMAGE_VAULT.getImageIcon("help")
        self.help_button.setIcon(self.help_button_icon)

        self.help_button.clicked.connect(lambda: self.container.setPage(Page.Help))
        self.page_buttons.append(self.help_button)

        # < page buttons - quit > #
        self.quit_button = QPushButton("Quit")

        self.quit_button_icon = APP_IMAGE_VAULT.getImageIcon("closed")
        self.quit_button.setIcon(self.quit_button_icon)

        self.quit_button.clicked.connect(lambda: self.app.quit())
        self.page_buttons.append(self.quit_button)

        # < page buttons - add to page > #
        row: int = 1
        column: int = 0

        for button in self.page_buttons:
            button.setObjectName("homeButton")
            button.setFixedSize(self.container.button_size)

            button.setIconSize(self.container.icon_size)

            self.page_layout.addWidget(
                button,
                row,
                column,
                1,
                2,
                Qt.AlignmentFlag.AlignCenter,
            )

            if column == 2:
                row = row + 1
                column = 0
            else:
                column = 2

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
