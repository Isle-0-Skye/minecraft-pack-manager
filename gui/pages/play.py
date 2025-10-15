from minecraft_pack_manager.gui.container import Container
from minecraft_pack_manager.gui.page import BasePage, Page
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton


# < ----------------------------------------------------------------------- > #


class PlayPage(BasePage):
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
        self.title = QLabel("Play")
        self.title.setObjectName("pageTitle")
        self.title.setFixedSize(self.container.title_size)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_layout.addWidget(self.title, 0, 0, 1, 4, self.container.title_alignment)

        # < page buttons > #
        # < page buttons - home > #
        self.home_button = QPushButton("Back")
        self.home_button.setFixedSize(self.container.secondary_button_size)

        self.home_button.clicked.connect(lambda: self.container.setPage(Page.Home))
        self.page_layout.addWidget(self.home_button, 3, 3)

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
