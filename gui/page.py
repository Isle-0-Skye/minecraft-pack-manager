from enum import Enum

from PySide6.QtWidgets import QApplication, QWidget


# < ----------------------------------------------------------------------- > #


class Page(Enum):
    Home = 0
    Upload = 1
    Download = 2
    Play = 3
    Settings = 4
    Help = 5


# < ----------------------------------------------------------------------- > #


class BasePage(QWidget):
    def __init__(self, app: QApplication, container) -> None:
        super().__init__()

        # < attributes > #
        self.app: QApplication = app
        self.container = container


# < ----------------------------------------------------------------------- > #
