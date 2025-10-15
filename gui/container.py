from minecraft_pack_manager import APP_PACKAGE
from minecraft_pack_manager.gui.page import BasePage, Page
from minecraft_pack_manager.lib.settings import APP_IMAGE_VAULT
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QWidget,
)


# < ----------------------------------------------------------------------- > #


class Container(QWidget):
    def __init__(self, app: QApplication, window: QMainWindow) -> None:
        super().__init__()

        # < attributes > #
        self.app_window: QMainWindow = window
        self.app: QApplication = app

        self.title_alignment = Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop

        self.title_size = QSize(384, 56)

        self.button_size = QSize(256, 72)
        self.secondary_button_size = QSize(160, 40)

        self.icon_size = QSize(56, 56)
        self.secondary_icon_size = QSize(32, 32)

        # < layout - margins > #
        self.setContentsMargins(0, 0, 0, 0)

        # < layout - window size > #
        self.setFixedSize(self.app_window.size())

        # < layout - widgets > #
        self.page_layout = QGridLayout()
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.page_layout)

        # < styling > #
        self.setWindowIcon(APP_IMAGE_VAULT.getImageIcon("mpm"))
        self.setStyleSheet(APP_PACKAGE.getConfig().getStylesheet())

        # < widgets > #
        # < widgets - background image > #
        self.background_image = APP_IMAGE_VAULT.getImagePixmap("background")
        self.background_image.scaled(self.app_window.size())

        # < a label is used to display the image > #
        self.background = QLabel()
        self.background.setObjectName("background")
        self.background.setFixedSize(self.app_window.size())

        self.background.setPixmap(self.background_image)

        self.page_layout.addWidget(self.background, 0, 0)

        # < widgets - pages > #
        # < stack pages ontop one another > #
        # < show one at a time > #
        self.pages = QStackedWidget()
        self.pages.setFixedSize(self.app_window.size())
        self.page_layout.addWidget(self.pages, 0, 0)

    # < ------------------------------------------------------------------- > #

    def addPage(self, page: type[BasePage]) -> None:
        self.pages.addWidget(page(app=self.app, container=self))

    # < ------------------------------------------------------------------- > #

    def setPage(self, page: Page) -> None:
        self.pages.setCurrentIndex(page.value)

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
