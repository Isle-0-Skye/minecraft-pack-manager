import sys

from minecraft_pack_manager import APP_LOGGER, APP_PACKAGE, APP_PATHS
from minecraft_pack_manager.gui.container import Container
from minecraft_pack_manager.gui.page import BasePage
from minecraft_pack_manager.gui.pages.download import DownloadPage
from minecraft_pack_manager.gui.pages.help import HelpPage
from minecraft_pack_manager.gui.pages.home import HomePage
from minecraft_pack_manager.gui.pages.play import PlayPage
from minecraft_pack_manager.gui.pages.settings import SettingsPage
from minecraft_pack_manager.gui.pages.upload import UploadPage
from minecraft_pack_manager.lib.settings import APP_FONT_VAULT, APP_IMAGE_VAULT
from photon.lib.paths import Paths
from PySide6.QtCore import QDir, QSize
from PySide6.QtWidgets import QApplication, QMainWindow


# < ----------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #


def main() -> int:
    name = "Minecraft Pack Manager"
    version = "1.0.1"
    window_title: str = f"{name} {version}"

    width = 720
    height = 400
    window_size = QSize(width, height)

    application = QApplication(sys.argv)

    for entry in APP_PATHS.root().joinpath("third_party", "qt", "plugins").rglob("*"):
        extension: list[str] = entry.name.split(entry.stem)

        if extension.__len__() < 2:
            extension.insert(0, "")

        if extension[1] in [".so", ".dll"]:
            APP_LOGGER.debug(f"loading {extension[1]}: {entry}")
            application.addLibraryPath(entry.resolve().as_posix())

    mpm = MinecraftPackManager(window_title, window_size, application)
    mpm.show()

    return application.exec_()


# < ----------------------------------------------------------------------- > #


class MinecraftPackManager(QMainWindow):
    def __init__(self, window_title: str, window_size: QSize, app: QApplication) -> None:
        super().__init__()

        # < attributes > #
        self.window_title: str = window_title
        self.window_size: QSize = window_size
        self.app: QApplication = app

        # < layout - margins> #
        self.setContentsMargins(0, 0, 0, 0)

        # < layout - window size > #
        self.setFixedSize(self.window_size)

        # < layout - window title > #
        self.setWindowTitle(self.window_title)

        # < load images > #
        QDir.addSearchPath("images", APP_PATHS.images())
        APP_IMAGE_VAULT.loadFromPath(Paths("photon").images())
        APP_IMAGE_VAULT.loadFromPath(APP_PATHS.images())

        # < load fonts > #
        APP_FONT_VAULT.loadFromPath(Paths("photon").fonts())
        APP_FONT_VAULT.loadFromPath(APP_PATHS.fonts())
        APP_FONT_VAULT.reloadFontDatabase()

        # < styling > #
        self.setWindowIcon(APP_IMAGE_VAULT.getImageIcon("mpm"))
        self.setStyleSheet(APP_PACKAGE.getConfig().getStylesheet())

        # < container > #
        container = Container(self.app, self)
        self.setCentralWidget(container)

        # < add all pages > #
        pages: tuple[type[BasePage]] = (
            HomePage,
            UploadPage,
            DownloadPage,
            PlayPage,
            SettingsPage,
            HelpPage,
        )

        for page in pages:
            container.addPage(page)

    # < ------------------------------------------------------------------- > #


# < ----------------------------------------------------------------------- > #
