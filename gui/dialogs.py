from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QWidget


# < ----------------------------------------------------------------------- > #


class BaseDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        message: str = "default message",
        accept_text: str = "Ok",
        accept_show: bool = True,
        reject_text: str = "Close",
        reject_show: bool = True,
        accept_column: int = 0,
        reject_column: int = 1,
    ) -> None:
        super().__init__(parent)

        # < attributes > #
        self.dialog_size = QSize(360, 120)
        self.message = message

        self.accept_text = accept_text
        self.accept_show = accept_show
        self.accept_column = accept_column

        self.reject_text = reject_text
        self.reject_show = reject_show
        self.reject_column = reject_column

        self.baseSetup()

    # < ------------------------------------------------------------------- > #

    def baseSetup(self) -> None:
        # < layout - margins > #
        self.setContentsMargins(0, 0, 0, 0)

        # < layout - page size > #
        self.setFixedSize(self.dialog_size)

        # < layout - widgets > #
        self.page_layout = QGridLayout()
        self.page_layout.setContentsMargins(8, 0, 8, 8)
        self.setLayout(self.page_layout)

        # < layout - dialog title > #
        self.setWindowTitle(" ")

        # < dialog label > #
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)

        self.page_layout.addWidget(self.message_label, 0, 0, 2, 2)

        # < dialog ok / accept button > #
        # < returns 1 > #
        self.accept_button = QPushButton(self.accept_text)
        self.accept_button.clicked.connect(self.accept)

        if self.accept_show:
            self.page_layout.addWidget(self.accept_button, 2, self.accept_column)

        # < dialog close / cancel / reject button > #
        # < returns 0 > #
        self.reject_button = QPushButton(self.reject_text)
        self.reject_button.clicked.connect(self.reject)

        if self.reject_show:
            self.page_layout.addWidget(self.reject_button, 2, self.reject_column)


# < ----------------------------------------------------------------------- > #


class SettingDialog(BaseDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        message: str = "Default Text",
        accept_text: str = "Ok",
        accept_show: bool = False,
    ) -> None:
        super().__init__(
            parent=parent, message=message, accept_text=accept_text, accept_show=accept_show
        )


# < ----------------------------------------------------------------------- > #


class ValidSettingDialog(SettingDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        message: str = "Valid Setting",
        accept_text: str = "Ok",
        accept_show: bool = False,
    ) -> None:
        super().__init__(
            parent=parent, message=message, accept_text=accept_text, accept_show=accept_show
        )


# < ----------------------------------------------------------------------- > #


class InvalidSettingDialog(SettingDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        message: str = "Invalid Setting",
        accept_text: str = "Ok",
        accept_show: bool = False,
    ) -> None:
        super().__init__(
            parent=parent, message=message, accept_text=accept_text, accept_show=accept_show
        )


# < ----------------------------------------------------------------------- > #
