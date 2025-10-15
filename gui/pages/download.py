from dataclasses import dataclass

from minecraft_pack_manager.gui.container import Container
from minecraft_pack_manager.gui.page import BasePage, Page
from minecraft_pack_manager.lib import transfer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QGridLayout, QLabel, QPushButton


# < ----------------------------------------------------------------------- > #


@dataclass
class RemoteInfo:
    remote: str
    upstreams: list[str]
    paths: list[str]
    names: list[str]


# < ----------------------------------------------------------------------- > #


class DownloadPage(BasePage):
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
        self.title = QLabel("Download")
        self.title.setObjectName("pageTitle")
        self.title.setFixedSize(self.container.title_size)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_layout.addWidget(self.title, 0, 0, 1, 4, self.container.title_alignment)

        # < page widgets > #
        # < page widgets - source label > #
        self.source_label = QLabel("Source:")
        self.source_label.setFixedSize(self.container.secondary_button_size)

        self.page_layout.addWidget(self.source_label, 1, 0)

        # < page widgets - source input > #
        self.source_input = QComboBox()
        self.source_input.setFixedHeight(self.container.secondary_button_size.height())

        self.page_layout.addWidget(self.source_input, 1, 1, 1, 3)

        # < page widgets - destination label > #
        self.destination_label = QLabel("Destination:")
        self.destination_label.setFixedSize(self.container.secondary_button_size)

        self.page_layout.addWidget(self.destination_label, 2, 0)

        # < page widgets - destination input > #
        self.destination_input = QComboBox()
        self.destination_input.setFixedHeight(self.container.secondary_button_size.height())

        self.destination_input.addItem("Make New Folder")

        self.page_layout.addWidget(self.destination_input, 2, 1, 1, 3)

        # < page widgets - refresh button > #
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFixedSize(self.container.secondary_button_size)

        self.refresh_button.clicked.connect(lambda: self.refreshLists())
        self.page_layout.addWidget(self.refresh_button, 3, 1)

        # < page widgets - continue button > #
        self.continue_button = QPushButton("Continue")
        self.continue_button.setFixedSize(self.container.secondary_button_size)

        self.continue_button.clicked.connect(lambda: self.continueTransfer())
        self.page_layout.addWidget(self.continue_button, 3, 2)

        # < page widgets - home button > #
        self.home_button = QPushButton("Back")
        self.home_button.setFixedSize(self.container.secondary_button_size)

        self.home_button.clicked.connect(lambda: self.container.setPage(Page.Home))
        self.page_layout.addWidget(self.home_button, 3, 3)

    # < ------------------------------------------------------------------- > #

    def refreshLists(self) -> None:
        transfer.updateListFromRemote(self.source_input)
        transfer.updateListFromLocal(self.destination_input)

    # < ------------------------------------------------------------------- > #

    def continueTransfer(self) -> None:
        transfer.transfer(self.source_input, self.destination_input)

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
